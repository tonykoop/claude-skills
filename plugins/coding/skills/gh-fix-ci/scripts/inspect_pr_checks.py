#!/usr/bin/env python3
"""Inspect failing GitHub PR checks and surface actionable GitHub Actions logs.

Uses the `gh` CLI. GitHub Actions checks are inspected for failure snippets;
non-GitHub-Actions checks (e.g. Buildkite) are reported as external with only
their details URL — never driven.

Exits non-zero when failing checks remain, so it is usable in automation.

Examples:
    inspect_pr_checks.py --repo . --pr 123
    inspect_pr_checks.py --repo . --pr https://github.com/org/repo/pull/123 --json
    inspect_pr_checks.py --repo . --max-lines 200 --context 40
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from typing import Any


def run(args: list[str], cwd: str) -> tuple[int, str, str]:
    proc = subprocess.run(
        args, cwd=cwd, capture_output=True, text=True
    )
    return proc.returncode, proc.stdout, proc.stderr


def gh_json(args: list[str], cwd: str) -> Any:
    code, out, err = run(["gh", *args], cwd)
    if code != 0:
        raise RuntimeError(f"gh {' '.join(args)} failed: {err.strip()}")
    return json.loads(out) if out.strip() else None


def resolve_pr(repo: str, pr: str | None) -> str:
    """Return a PR number as a string. Defaults to the current branch's PR."""
    if pr:
        m = re.search(r"/pull/(\d+)", pr)
        if m:
            return m.group(1)
        return pr.lstrip("#")
    data = gh_json(["pr", "view", "--json", "number,url"], repo)
    if not data or "number" not in data:
        raise RuntimeError("could not resolve a PR for the current branch")
    return str(data["number"])


def pr_checks(repo: str, pr: str) -> list[dict]:
    """gh pr checks with graceful field-drift fallback."""
    fields = "name,state,bucket,link,startedAt,completedAt,workflow"
    code, out, err = run(["gh", "pr", "checks", pr, "--json", fields], repo)
    if code != 0:
        # Field drift: retry without the optional fields gh complains about.
        code, out, err = run(["gh", "pr", "checks", pr, "--json", "name,state,link"], repo)
        if code != 0 and not out.strip():
            # gh exits non-zero when checks are failing; still emits JSON.
            if not out.strip():
                raise RuntimeError(f"gh pr checks failed: {err.strip()}")
    try:
        return json.loads(out) if out.strip() else []
    except json.JSONDecodeError:
        return []


def is_failing(check: dict) -> bool:
    state = (check.get("state") or check.get("bucket") or "").lower()
    return state in {"failure", "fail", "failing", "error", "cancelled", "timed_out"}


def run_id_from_link(link: str | None) -> str | None:
    if not link:
        return None
    if "github.com" not in link or "/actions/runs/" not in link:
        return None  # external provider (e.g. Buildkite) — not GitHub Actions
    m = re.search(r"/actions/runs/(\d+)", link)
    return m.group(1) if m else None


def failure_snippet(log: str, max_lines: int, context: int) -> str:
    lines = log.splitlines()
    err_re = re.compile(r"\b(error|fail(ed|ure)?|exception|traceback|assert)\b", re.I)
    hits = [i for i, ln in enumerate(lines) if err_re.search(ln)]
    if not hits:
        return "\n".join(lines[-max_lines:])
    start = max(0, hits[0] - context)
    end = min(len(lines), hits[-1] + context + 1)
    snippet = lines[start:end]
    if len(snippet) > max_lines:
        snippet = snippet[-max_lines:]
    return "\n".join(snippet)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", default=".", help="path inside the repo (default .)")
    ap.add_argument("--pr", default=None, help="PR number or URL (default: current branch)")
    ap.add_argument("--max-lines", type=int, default=120, help="max log lines in a snippet")
    ap.add_argument("--context", type=int, default=20, help="context lines around an error")
    ap.add_argument("--json", action="store_true", help="machine-friendly JSON output")
    args = ap.parse_args()

    # Auth check first — fail clearly if unauthenticated.
    code, _, _ = run(["gh", "auth", "status"], args.repo)
    if code != 0:
        print("gh is not authenticated. Run `gh auth login` (repo + workflow scopes).",
              file=sys.stderr)
        return 2

    pr = resolve_pr(args.repo, args.pr)
    checks = pr_checks(args.repo, pr)
    failing = [c for c in checks if is_failing(c)]

    results: list[dict] = []
    for c in failing:
        name = c.get("name") or c.get("workflow") or "<unknown>"
        link = c.get("link")
        rid = run_id_from_link(link)
        entry: dict = {"name": name, "link": link}
        if rid is None:
            entry["kind"] = "external"
            entry["note"] = "non-GitHub-Actions check; reporting URL only"
            results.append(entry)
            continue
        entry["kind"] = "github-actions"
        entry["run_id"] = rid
        code, log, err = run(["gh", "run", "view", rid, "--log"], args.repo)
        if code != 0 or not log.strip():
            entry["snippet"] = None
            entry["note"] = "log unavailable (run may still be in progress)"
        else:
            entry["snippet"] = failure_snippet(log, args.max_lines, args.context)
        results.append(entry)

    if args.json:
        print(json.dumps({"pr": pr, "failing": results}, indent=2))
    else:
        if not failing:
            print(f"PR #{pr}: no failing checks.")
        else:
            print(f"PR #{pr}: {len(failing)} failing check(s).\n")
            for r in results:
                print(f"=== {r['name']} ({r['kind']}) ===")
                if r.get("link"):
                    print(f"  url: {r['link']}")
                if r["kind"] == "external":
                    print("  external provider — not inspected (report URL only).\n")
                    continue
                if r.get("snippet"):
                    print(r["snippet"])
                else:
                    print(f"  {r.get('note', 'no snippet')}")
                print()

    return 1 if failing else 0


if __name__ == "__main__":
    sys.exit(main())
