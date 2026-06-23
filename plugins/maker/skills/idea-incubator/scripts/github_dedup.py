#!/usr/bin/env python3
"""GitHub-level chat-ID dedup for the idea-incubator dispatch pipeline.

Story #410 (Epic #406). Answers the question: "has this conversation already
been filed as a GitHub epic?" by checking for a `chat-id:<sha8>` label on any
open issue in the target repo.

Callers receive a `decide_mode()` answer — CREATE or APPEND — and act
accordingly without having to parse GitHub JSON themselves.

Design notes
------------
* **Offline-first**: the module works with no network if the caller only calls
  `chat_id_label()`. Only `find_epic_by_chat_id()` hits the network (via the
  `gh` CLI subprocess).
* **Safe fallback**: subprocess errors (gh not installed, auth expired, network
  outage) always return CREATE — better to potentially file a duplicate than to
  silently swallow a brainstorm.
* **Stable label format**: `chat-id:<sha8>` where sha8 = first 8 hex chars of
  sha256(conversation_id). Labels must not contain colons in some contexts;
  verify your GitHub label config. The format mirrors the fingerprint scheme
  used in `gemini_to_github.py`.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from typing import Literal


def chat_id_label(conversation_id: str) -> str:
    """Return the GitHub label string for a conversation ID.

    >>> chat_id_label("abc123")
    'chat-id:6ca13d52'
    """
    sha8 = hashlib.sha256(conversation_id.encode("utf-8")).hexdigest()[:8]
    return f"chat-id:{sha8}"


def find_epic_by_chat_id(repo: str, chat_id: str) -> int | None:
    """Search *repo* for an open issue labelled *chat_id*.

    Parameters
    ----------
    repo:
        GitHub repo in ``OWNER/REPO`` form.
    chat_id:
        The full label string, e.g. ``"chat-id:6ca13d52"``.

    Returns
    -------
    The issue number of the first matching open issue, or ``None`` if no match
    or if the `gh` CLI call fails (safe fallback).
    """
    try:
        result = subprocess.run(
            [
                "gh", "issue", "list",
                "--repo", repo,
                "--label", chat_id,
                "--state", "open",
                "--json", "number",
                "--limit", "1",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        sys.stderr.write(f"[github_dedup] gh CLI unavailable: {exc}\n")
        return None

    if result.returncode != 0:
        sys.stderr.write(
            f"[github_dedup] gh issue list failed (exit {result.returncode}): "
            f"{result.stderr.strip()}\n"
        )
        return None

    try:
        items: list[dict] = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        sys.stderr.write(f"[github_dedup] could not parse gh output: {exc}\n")
        return None

    if not items:
        return None
    return int(items[0]["number"])


def decide_mode(
    repo: str,
    conversation_id: str,
) -> Literal["CREATE", "APPEND"]:
    """Return ``"APPEND"`` if an open epic for *conversation_id* exists in *repo*,
    otherwise ``"CREATE"``.

    Errors in the GitHub lookup fall back to ``"CREATE"`` (safe-by-default).
    """
    label = chat_id_label(conversation_id)
    issue_num = find_epic_by_chat_id(repo, label)
    if issue_num is not None:
        sys.stderr.write(
            f"[github_dedup] found existing epic #{issue_num} for {label} → APPEND\n"
        )
        return "APPEND"
    return "CREATE"
