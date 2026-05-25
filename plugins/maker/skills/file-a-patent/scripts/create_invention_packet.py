#!/usr/bin/env python3
"""Create a private invention packet from bundled Markdown templates."""

from __future__ import annotations

import argparse
import datetime as dt
import shutil
import subprocess
from pathlib import Path


TEMPLATE_DIR = Path(__file__).resolve().parents[1] / "assets" / "templates" / "invention-packet"


def slugify(value: str) -> str:
    cleaned = []
    last_dash = False
    for ch in value.lower().strip():
        if ch.isalnum():
            cleaned.append(ch)
            last_dash = False
        elif not last_dash:
            cleaned.append("-")
            last_dash = True
    return "".join(cleaned).strip("-") or "invention"


def git_head(repo: Path) -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(repo), "rev-parse", "--short", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return "TODO"


def render(text: str, values: dict[str, str]) -> str:
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def main() -> int:
    parser = argparse.ArgumentParser(description="Create an invention packet scaffold.")
    parser.add_argument("--repo", required=True, help="Local repo path or evidence folder")
    parser.add_argument("--output-root", required=True, help="Directory that will contain packet folders")
    parser.add_argument("--candidate", default="", help="Human-readable invention candidate name")
    parser.add_argument("--slug", default="", help="Packet folder slug; defaults to repo name")
    parser.add_argument(
        "--mode",
        choices=["provisional-prep", "strategy-hold", "trade-secret-review", "copyright-docs"],
        default="provisional-prep",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite an existing packet folder")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    output_root = Path(args.output_root).resolve()
    slug = slugify(args.slug or repo.name)
    candidate = args.candidate or repo.name
    packet_dir = output_root / slug

    if packet_dir.exists() and not args.force:
        raise SystemExit(f"Packet exists: {packet_dir} (use --force to overwrite)")
    if packet_dir.exists():
        shutil.rmtree(packet_dir)

    packet_dir.mkdir(parents=True, exist_ok=True)

    values = {
        "repo_name": repo.name,
        "repo_path": str(repo),
        "candidate_name": candidate,
        "packet_slug": slug,
        "packet_mode": args.mode,
        "created_date": dt.date.today().isoformat(),
        "git_head": git_head(repo),
    }

    for template in sorted(TEMPLATE_DIR.glob("*.md")):
        target = packet_dir / template.name
        target.write_text(render(template.read_text(encoding="utf-8"), values), encoding="utf-8")

    print(packet_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
