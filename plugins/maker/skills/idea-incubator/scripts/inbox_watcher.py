#!/usr/bin/env python3
"""File-watcher daemon + verbal-trigger regex for the idea-incubator inbox.

Story #409 (Epic #406). Polls the Obsidian vault inbox folder for new or
modified .md files and fires the ingestion pipeline when a verbal trigger is
detected in the file content.

Design goals
------------
* **No external deps** — uses stdlib `os.scandir` polling; no `watchdog` package.
* **Verbal triggers** — regex patterns matching the skill's trigger phrases so
  the watcher picks up voice-to-text brainstorms that include an explicit "incubate
  this" / "new idea" signal rather than firing on every dropped file.
* **Dry-run friendly** — `--once` + `--dry-run` prints what would be dispatched.
* **Resumable** — processed files are stamped by the downstream script
  (append_mode.py), not re-fired on re-scan.

Trigger logic
-------------
A file is considered "actionable" when:
  1. It has a `.md` extension, and
  2. Its content matches at least one trigger pattern (see VERBAL_TRIGGERS), OR
     the `--no-trigger-check` flag is set (dispatch all new files unconditionally).

The verbal trigger check is a lightweight regex pass over the raw file content —
not an LLM call. It matches the skill's canonical trigger phrases so the watcher
fires only on intentional brainstorm clips, not on every random Obsidian file
dropped into the inbox.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------
# Verbal trigger patterns — mirrors the trigger phrases in SKILL.md
# ---------------------------------------------------------------------------

_RAW_TRIGGERS: list[str] = [
    r"incubate\s+this",
    r"new\s+idea",
    r"add\s+this\s+to\s+(my\s+)?inbox",
    r"process\s+(my\s+)?inbox",
    r"file\s+gh\s+issues",
    r"ingest\s+this\s+brainstorm",
    r"break\s+this\s+into\s+epics",
    r"here.s\s+my\s+(next\s+)?brainstorming\s+doc",
    r"review\s+my\s+ideas",
    r"red.?team\s+this",
    r"capture\s+from\s+mobile",
    r"obsidian\s+clip",
    # Also fire when the file body contains the fingerprint marker — it was
    # clipped by the mobile bridge and needs pipeline processing.
    r"<!--\s*idea-fingerprint:",
    # Files produced by the mobile bridge stub always have this source line.
    r"source:\s*gemini",
]

VERBAL_TRIGGERS: list[re.Pattern[str]] = [
    re.compile(p, re.IGNORECASE | re.MULTILINE) for p in _RAW_TRIGGERS
]


def detect_triggers(content: str) -> list[str]:
    """Return list of raw trigger patterns that matched *content*."""
    return [p.pattern for p in VERBAL_TRIGGERS if p.search(content)]


# ---------------------------------------------------------------------------
# Watcher state
# ---------------------------------------------------------------------------


@dataclass
class WatcherState:
    """Lightweight mutable state for a single watcher run."""

    # Maps path → last-seen mtime so we detect new files and modifications.
    seen: dict[str, float] = field(default_factory=dict)


@dataclass
class ScanResult:
    """Result of a single inbox scan."""

    new_files: list[Path] = field(default_factory=list)
    triggered: list[Path] = field(default_factory=list)
    skipped_no_trigger: list[Path] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Core watcher logic
# ---------------------------------------------------------------------------


def scan_once(
    inbox_dir: Path,
    state: WatcherState,
    *,
    no_trigger_check: bool = False,
    extensions: tuple[str, ...] = (".md",),
) -> ScanResult:
    """Scan *inbox_dir* for new or modified files since the last call.

    Parameters
    ----------
    inbox_dir:
        The Obsidian vault inbox folder to watch.
    state:
        Mutable state tracking previously-seen file mtimes. Pass the same
        instance across calls so the watcher detects changes incrementally.
    no_trigger_check:
        If True, every new/modified file is treated as triggered (no regex check).
    extensions:
        File extensions to consider. Default is `('.md',)`.

    Returns
    -------
    ScanResult with lists of new files, triggered files, and skipped files.
    """
    result = ScanResult()

    if not inbox_dir.is_dir():
        return result

    try:
        entries = list(os.scandir(inbox_dir))
    except PermissionError:
        return result

    for entry in entries:
        if not entry.is_file():
            continue
        path = Path(entry.path)
        if path.suffix.lower() not in extensions:
            continue

        try:
            mtime = entry.stat().st_mtime
        except OSError:
            continue

        prev_mtime = state.seen.get(str(path))
        if prev_mtime is not None and mtime <= prev_mtime:
            continue  # unchanged since last scan

        state.seen[str(path)] = mtime
        result.new_files.append(path)

        if no_trigger_check:
            result.triggered.append(path)
            continue

        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            result.skipped_no_trigger.append(path)
            continue

        if detect_triggers(content):
            result.triggered.append(path)
        else:
            result.skipped_no_trigger.append(path)

    return result


def dispatch_file(
    pipeline_cmd: list[str],
    file_path: Path,
    *,
    dry_run: bool = False,
    timeout: int = 300,
) -> bool:
    """Fire the pipeline command for *file_path*.

    The command template may contain the literal ``{file}`` which is replaced
    by the absolute path of the file. If no ``{file}`` placeholder is present,
    the path is appended as the last argument.

    Returns True on success (or dry-run), False on subprocess failure.
    """
    file_str = str(file_path.resolve())
    cmd = [arg.replace("{file}", file_str) for arg in pipeline_cmd]
    if "{file}" not in " ".join(pipeline_cmd):
        cmd.append(file_str)

    if dry_run:
        sys.stdout.write(f"[dry-run] would dispatch: {' '.join(cmd)}\n")
        return True

    try:
        result = subprocess.run(cmd, timeout=timeout, check=False)
        if result.returncode != 0:
            sys.stderr.write(
                f"[warn] pipeline returned {result.returncode} for {file_path.name}\n"
            )
            return False
        return True
    except subprocess.TimeoutExpired:
        sys.stderr.write(f"[warn] pipeline timeout for {file_path.name}\n")
        return False
    except OSError as exc:
        sys.stderr.write(f"[error] could not launch pipeline: {exc}\n")
        return False


# ---------------------------------------------------------------------------
# InboxWatcher
# ---------------------------------------------------------------------------


class InboxWatcher:
    """Polling-based file watcher for the Obsidian vault inbox.

    Parameters
    ----------
    inbox_dir:
        Vault inbox directory to watch.
    pipeline_cmd:
        Shell command tokens to run per triggered file. Use ``{file}`` as a
        placeholder for the file path; if absent, the path is appended.
    interval_s:
        Poll interval in seconds (default 5).
    no_trigger_check:
        If True, fire for every new/modified file regardless of content.
    dry_run:
        If True, print dispatch commands instead of running them.
    """

    def __init__(
        self,
        inbox_dir: Path,
        pipeline_cmd: list[str],
        *,
        interval_s: float = 5.0,
        no_trigger_check: bool = False,
        dry_run: bool = False,
    ) -> None:
        self.inbox_dir = inbox_dir
        self.pipeline_cmd = pipeline_cmd
        self.interval_s = interval_s
        self.no_trigger_check = no_trigger_check
        self.dry_run = dry_run
        self._state = WatcherState()

    def scan_once(self) -> ScanResult:
        return scan_once(
            self.inbox_dir, self._state, no_trigger_check=self.no_trigger_check
        )

    def run_once(self) -> ScanResult:
        """Run one scan and dispatch triggered files."""
        result = self.scan_once()
        for path in result.triggered:
            dispatch_file(self.pipeline_cmd, path, dry_run=self.dry_run)
        return result

    def run_forever(self) -> None:
        """Poll indefinitely; Ctrl-C to stop."""
        sys.stderr.write(
            f"[watch] polling {self.inbox_dir} every {self.interval_s}s "
            f"(trigger-check={'off' if self.no_trigger_check else 'on'})\n"
        )
        try:
            while True:
                result = self.run_once()
                for p in result.triggered:
                    sys.stderr.write(f"[dispatch] {p.name}\n")
                for p in result.skipped_no_trigger:
                    sys.stderr.write(f"[skip] {p.name} (no trigger)\n")
                time.sleep(self.interval_s)
        except KeyboardInterrupt:
            sys.stderr.write("\n[watch] stopped.\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "inbox_dir",
        type=Path,
        nargs="?",
        default=Path("00-inbox"),
        help="Obsidian vault inbox folder to watch (default: 00-inbox).",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Scan once and exit (default: poll forever).",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=5.0,
        metavar="SECONDS",
        help="Poll interval in seconds (default: 5).",
    )
    parser.add_argument(
        "--pipeline-cmd",
        nargs="+",
        default=["python", "-m", "gemini_to_github", "{file}"],
        metavar="ARG",
        help="Pipeline command to run per triggered file. Use {file} as path placeholder.",
    )
    parser.add_argument(
        "--no-trigger-check",
        action="store_true",
        help="Fire for every new/modified file without checking for verbal triggers.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print dispatch commands instead of running them.",
    )
    parser.add_argument(
        "--list-triggers",
        action="store_true",
        help="Print all verbal trigger patterns and exit.",
    )
    args = parser.parse_args(argv[1:])

    if args.list_triggers:
        for p in _RAW_TRIGGERS:
            print(p)
        return 0

    watcher = InboxWatcher(
        inbox_dir=args.inbox_dir,
        pipeline_cmd=args.pipeline_cmd,
        interval_s=args.interval,
        no_trigger_check=args.no_trigger_check,
        dry_run=args.dry_run,
    )

    if args.once:
        result = watcher.run_once()
        sys.stdout.write(
            f"[scan] new={len(result.new_files)} "
            f"triggered={len(result.triggered)} "
            f"skipped={len(result.skipped_no_trigger)}\n"
        )
        for p in result.triggered:
            sys.stdout.write(f"  [triggered] {p.name}\n")
        for p in result.skipped_no_trigger:
            sys.stdout.write(f"  [skipped]   {p.name}\n")
        return 0

    watcher.run_forever()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
