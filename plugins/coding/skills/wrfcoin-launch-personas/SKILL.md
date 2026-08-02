---
name: wrfcoin-launch-personas
description: Launch WRFCoin personas in independent Codex or Claude sessions from a sprint document and persona manifest. Use when the user wants Alice, Bob, Cindy, Dan, Elsa, Frank, or Gina to run in parallel with their own visible terminals or tmux windows.
---

# WRFCoin Launch Personas

This is the Codex-side replacement for the older Claude-only tmux launch flow.

## What changed

- The sprint doc now uses per-persona sections, not the older assignment table.
- A persona can be owned by either Codex or Claude for the session.
- The launcher must support visible terminals, not just headless logs.

## Launch modes

Use `scripts/launch-personas.sh` with one of:

- `tmux`: one window per persona inside a tmux session
- `wt`: one Windows Terminal tab per persona through `wt.exe`
- `background`: detached processes with log files

## Inputs

- sprint document path
- persona manifest TSV
- optional mode override

The manifest maps each persona to:

- runtime: `codex` or `claude`
- repo directory
- team mode: `sprint-ops`, `quality-gate`, or `cross-repo-integration`
- model and effort
- optional prompt file

## Rules

- Do not assign the same persona to both runtimes.
- Use one repo root per persona session.
- If a prompt file is supplied, load it; otherwise generate a prompt from the sprint doc and team mode.
- For audit teams, keep runs read-only unless the prompt explicitly calls for fixes.

## Team references

Before launching, read:

- `../wrfcoin-agent-teams/SKILL.md`
- `../wrfcoin-agent-teams/references/team-topologies.md`

## Suggested manifest

Use `docs/plans/persona-launch.example.tsv` as the starting template.
