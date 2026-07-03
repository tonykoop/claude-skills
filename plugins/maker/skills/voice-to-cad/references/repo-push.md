# Stage 5 — Repo push (existing or new, GENERATED provenance)

The highway ends with the idea *versioned*, not just rendered. Two paths.

## Choosing

Ask once: "existing repo or new one?" If the object belongs to an existing
project family (an instrument variant, a shop fixture for a known repo),
push there. A genuinely new object gets a new repo. When unsure, name your
best-guess repo and let the user confirm — don't enumerate their whole
GitHub account.

## Existing repo

Land under a dated pipeline directory, never over source-of-truth dirs:

```
<repo>/voice-to-cad/<YYYY-MM-DD>-<slug>/
  design-brief.md
  concepts/            # 4 concept PNGs + vote-log.json
  candidate.scad
  candidate.stl
  preview.png
  provenance.json
  README.md            # one paragraph + GENERATED banner
```

Never write into `masters/`, `evolution/` intake, or measured-spec files —
generated artifacts don't touch reviewed authority. Commit message:
`feat(voice-to-cad): <object> concept→CAD pipeline run (generated, not a master)`.

## New repo

`gh repo create <owner>/<slug> --private` (private by default; the user can
flip it later — publishing is their call, not the pipeline's). Scaffold:

```
README.md          # what it is, vision paragraph from the brief, GENERATED banner
design-brief.md
concepts/  candidate.scad  candidate.stl  preview.png  provenance.json
.gitattributes     # * text=auto eol=lf + binary excludes (png, stl)
```

## provenance.json

```json
{
  "schema": "voice-to-cad-provenance-v1",
  "pipeline": "voice-to-cad 0.1.0",
  "stages": {
    "brief": {"gate": "user-approved", "constraints_stated": 4, "assumed": 2},
    "images": {"generator": "agy", "variants": 4, "cost_usd": 0.0},
    "tournament": {"votes": 3, "winner": "b", "synthesis": "angular > round"},
    "cad": {"tool": "CADAM + <model>", "conversation_id": "...",
             "cost_usd": 0.0, "wall_s": 0, "gate": {"pass_rate": 0.0,
             "misses": []}}
  },
  "labels": ["GENERATED", "not-a-measured-master"],
  "date": "<YYYY-MM-DD>"
}
```

## The gate

Before any push, one confirm containing: repo, path, file list, and the
GENERATED banner text. Pushing is outward-facing — no confirm, no push.
After pushing, hand the user the commit URL and the running cost total, and
offer the natural next handoffs (maker-engineering for DoE/validation,
instrument-maker or sheet-metal for real fabrication packets, evolution
pipeline for production-readiness).

## The banner (verbatim, in every README this skill writes)

> **GENERATED — not a measured master.** Produced by the voice-to-cad
> pipeline (brainstorm → image tournament → image-conditioned codeCAD).
> Dimensions labeled `assumed` in the brief are placeholders. Do not treat
> as reviewed fabrication authority.
