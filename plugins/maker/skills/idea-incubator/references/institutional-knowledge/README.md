# Institutional Knowledge (per-epic retro notes)

Story #240. This folder is the repo-side mirror of the Obsidian
`[Institutional Knowledge]` folder. It holds one **retro note per closed epic**,
produced by the retrospective sweep
([`../../scripts/retrospective_sweep.py`](../../scripts/retrospective_sweep.py))
and finished by the Retrospective / Lessons-Learned agent
([`../../agents/retrospective.md`](../../agents/retrospective.md)).

## Layout

- `epic-<N>-retro.md` — the human-readable retro note for epic `#N`. It opens
  with a `Source: epic #N` line and ends with a `## Backlink` section, so every
  note links back to the epic it came from (traceability requirement of #240).
- `epic-<N>-sweep.json` — the raw evidence the sweep gathered (child stories +
  states, referencing commits, PR references). Provenance for the note.

## How it relates to the aggregate store

The single-file aggregate store
([`../institutional-knowledge.md`](../institutional-knowledge.md)) remains the
**pre-read index**: the small, tag-filtered set of lessons the parser loads
before generating new epics. Per-epic retro notes in this folder are the **raw
material**. Workflow:

1. An epic closes → run the sweep → a `epic-<N>-retro.md` lands here.
2. The retrospective agent distills 1–3 transferable lessons into the note.
3. After the human accepts them, each lesson is appended (by hand, dated) to the
   aggregate store under its domain section — never auto-mutated.

This keeps the durable layer curated while preserving full per-epic evidence for
audit.
