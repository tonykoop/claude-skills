# TwinGrid + Partner Peek mode

A reusable round mode for the tmux sprint grid that pairs every lane with a
twin runtime (Claude **A** vs Codex **B**), runs a blind A/B pass, then runs a
structured Partner Peek pass where each side reads its partner's output and
produces a v2 supplement plus PR-ready skill recommendations.

This directory holds the **contract** that both `tmux-sprint` (Claude) and
`tmux-v2` (Codex) implement. The supporting scripts live under
[`../../scripts/twingrid/`](../../scripts/twingrid/).

## Why

Round 7 of the WRFCoin sprint dashboard ran a blind A/B + Partner Peek pass ad
hoc and produced measurably better artifacts than single-runtime rounds —
sharper uncertainty discipline, partner-validated suggestions, and explicit
skill-improvement proposals. The mode is now part of the sprint driver instead
of being re-derived in every manager prompt.

## Phases

1. **Blind A/B dispatch.** Manager dispatches the same lane task to side A and
   side B with handoffs from
   [`blind-handoff-template.md`](blind-handoff-template.md). Sides do not
   communicate. Each side writes outputs to a per-lane folder and finishes with
   an [agent record](agent-record.schema.yaml).
2. **Reveal brief.** Manager writes a single shared reveal brief (one file)
   listing partner-output paths and a one-paragraph A/B comparison per lane.
3. **Partner Peek.** Manager dispatches handoffs from
   [`partner-peek-handoff-template.md`](partner-peek-handoff-template.md). Each
   side reads its partner's folder, preserves originals, adds v2 supplements,
   validates with available tools, and writes
   `partner-peek-improvements.md` plus a partner-peek record.
4. **Lane matrix.** Manager runs
   [`scripts/twingrid/twingrid-lane-matrix.sh`](../../scripts/twingrid/twingrid-lane-matrix.sh)
   to produce a per-lane matrix (A path / B path / v2 path / validations run /
   skill-improvement recommendation).
5. **Block sweep.** Manager runs
   [`scripts/twingrid/twingrid-detect-blocked.sh`](../../scripts/twingrid/twingrid-detect-blocked.sh)
   to surface panes blocked on approval prompts, missing tools, or
   long-running validators.

## Manager-owned vs agent-owned data

The manager owns process telemetry; the agent owns content evidence. This
boundary stops self-reported numbers from drifting and lets the manager build
the lane matrix without re-asking each agent.

| Field | Owner | Source |
| --- | --- | --- |
| `elapsed_time` | manager | tmux pane timestamps |
| `context_remaining` | manager | runtime statusline scrape |
| `usage_remaining` | manager | runtime statusline scrape |
| `blocked_state` | manager | block-detection script |
| `actual_model` | agent | runtime self-report (one-shot) |
| `artifacts_produced` | agent | written into agent record |
| `validation_run` | agent | written into agent record |
| `partner_ideas_adopted` | agent | written into partner-peek record |
| `skill_improvement_recommendation` | agent | written into partner-peek record |

## Modes

The mode supports both **content-generation rounds** (e.g., reverse-engineer a
pack basket, design a chickadee birdhouse) and **skill-development rounds**
(e.g., implement an issue against a skill). The handoff templates carry the
same shape for both; only the assignment text varies.

## Files in this directory

| File | Purpose |
| --- | --- |
| [`blind-handoff-template.md`](blind-handoff-template.md) | Per-lane blind dispatch handoff. Manager fills the placeholders and writes one per side per lane. |
| [`partner-peek-handoff-template.md`](partner-peek-handoff-template.md) | Per-lane Partner Peek handoff after the reveal brief. |
| [`agent-record.schema.yaml`](agent-record.schema.yaml) | Required fields for the blind-pass agent record. |
| [`agent-record.example.json`](agent-record.example.json) | Worked example using Round 7 lane Henry side A. |
| [`partner-peek-record.schema.yaml`](partner-peek-record.schema.yaml) | Required fields for the Partner Peek record. |
| [`lane-matrix-row.schema.yaml`](lane-matrix-row.schema.yaml) | One row of the manager-owned lane matrix. |

## Folder-naming convention (enforced by lane-matrix)

The blind-handoff template prescribes:

```
/tmp/twingrid-r<N>-<runtime>-<lane>-<slug>
```

`twingrid-lane-matrix.sh` pairs A and B by `<lane>`. Folders whose names omit
the lane (e.g., `twingrid-r7-claude-A-pack-basket` instead of
`twingrid-r7-claude-henry-pack-basket`) land under `lane: unknown` and do not
pair correctly. The script intentionally enforces the convention rather than
guessing — drift here is a real signal that the dispatch handoff did not
specify the canonical folder name. Round 7's lane Henry blind-pass folder
was misnamed exactly this way and surfaces as the in-tree case study.

## Provenance

Round 7 evidence used to design this mode lives at
`/tmp/twingrid-r7-partner-peek.md` and `/tmp/twingrid-r7-*/partner-peek-*`
on the manager's machine.
