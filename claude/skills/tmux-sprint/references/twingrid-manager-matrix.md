# TwinGrid Manager Matrix

The manager matrix is a round-level view used after the blind pass, after
Partner Peek, and before opening skill-development PRs.

## Required columns

| Column | Source |
| --- | --- |
| lane | `agent_record.*`, `partner-peek-record.*`, or folder naming fallback |
| side | record field or folder naming fallback |
| runtime | record field or folder naming fallback |
| blind output folder | output folder path |
| blind artifacts | `artifacts_produced`, or files present before Partner Peek |
| v2 artifacts | `partner-peek-improvements.md`, `v2-*`, partner records |
| validation run | record `validation_run` plus detected validation logs |
| PR/issues opened | partner record or PR handoff field |
| skill recommendation | partner record recommendation fields |
| blocked pane state | pane-capture regex result |

## Block detection watch phrases

Pane captures should be scanned for:

- local command approval prompts: `Do you want to allow`, `requires approval`,
  `approve this command`, `waiting for approval`
- missing tools: `command not found`, `No such file or directory`,
  `not installed`, `missing tool`, `install hint`
- package/network blockers: `Temporary failure resolving`, `network is
  unreachable`, `403`, `401`, `rate limit`
- validator hangs: `watching for changes`, `Press Ctrl-C`, `waiting for input`

The detector should report the phrase family and pane/capture filename; the
manager decides whether to interrupt, approve, install, or re-dispatch.

## Script

Use the bundled script for a first-pass matrix:

```bash
python3 claude/skills/tmux-sprint/scripts/twingrid_matrix.py \
  --outputs-glob '/tmp/twingrid-r7-*' \
  --pane-captures-dir /tmp/twingrid-r7-pane-captures \
  --format json
```

The script emits a side-level `lanes` array, a grouped `lane_pairs` array, and
a `blocked_panes` array. It is deliberately filesystem-only so it can run after
a `/compact`, on a copied `/tmp` artifact bundle, or from a different manager
runtime.

## JSON shape

```json
{
  "lanes": [
    {
      "lane": "henry",
      "side": "B",
      "runtime": "codex",
      "output_folder": "/tmp/twingrid-r7-codex-henry-pack-basket",
      "blind_artifacts": ["reverse_engineering_report.md"],
      "v2_artifacts": ["partner-peek-improvements.md"],
      "validation_run": ["jq . partner-peek-record.json"],
      "skill_recommendation": "Add image-attachment preflight",
      "pr_or_issues_opened": "None"
    }
  ],
  "lane_pairs": [
    {
      "lane": "henry",
      "sides": {
        "A": {"output_folder": "/tmp/twingrid-r7-claude-A-pack-basket"},
        "B": {"output_folder": "/tmp/twingrid-r7-codex-henry-pack-basket"}
      }
    }
  ],
  "blocked_panes": [
    {
      "capture": "pane-3.txt",
      "block_type": "approval_prompt",
      "matched": "Do you want to allow"
    }
  ]
}
```
