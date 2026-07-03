# Stage 4 — codeCAD production (winning image + brief → parametric OpenSCAD)

This is the image-conditioned code-CAD lane proven on the 2026-07-02
instrument pilot series (fujara 1.000 on the objective gate). The canonical
deep reference lives in `reverse-engineer`'s
`references/parametric-recreation.md`; this file is the self-contained
version tuned for highway use (brief already exists, image is generated not
photographed).

## Tooling

- Local CADAM instance (github.com/Adam-CAD/CADAM; Tony's at `_meta/CADAM`,
  setup script `_meta/cadam-setup.sh`, notes `_meta/cadam-notes.md`) with a
  Claude model via OpenRouter. Model picker: choose the strongest available
  Claude; submit with **Enter in the textarea** (the sparkle button is a
  prompt enhancer, not submit); attach the winning concept image.
- Local OpenSCAD + BOSL2 (WSL: `~/.local/share/OpenSCAD/libraries/BOSL2`;
  Windows: `Documents\OpenSCAD\libraries\BOSL2`).

## The CAD prompt

Assemble from the brief + tournament synthesis:

1. "Use the attached concept render as visual inspiration." The image is
   *aesthetic authority*; the brief's numbers are *dimensional authority* —
   say so when they might conflict.
2. "Model <object> as ONE self-contained OpenSCAD program." BOSL2 available.
3. Distinct bodies: a named module per part from the brief's part list,
   "do not fuse across joints", top-level assembly module.
4. Every driving dimension as a named editable parameter with the brief's
   value: `bowl_diameter_mm (516)`.
5. Fabrication floors, stated plainly: "every solid wall ≥ <min_wall floor>;
   no decorative sub-millimeter features; fits <envelope> mm." Thin display
   geometry (strings, lattices, filigree) is the universal failure mode —
   ask for a `show_display_geometry` parameter when the design wants thin
   decoration, so a gate variant can disable it.
6. Placeholders declared as placeholders for anything the brief lists under
   Unknowns.
7. "$fn moderate (≤96) so the model compiles quickly" — compound curved
   surfaces at high $fn can take 10+ minutes; keep the highway fast.

## Extraction and compile

SCAD source of truth is CADAM's local Supabase, not the page DOM:

```bash
docker exec supabase_db_cadam psql -U postgres -d postgres -t -A -c \
 "SELECT part->'input'->>'code' FROM public.messages m,
  jsonb_array_elements(m.parts) part
  WHERE m.conversation_id='<conv-id>'
    AND part->'input'->>'code' IS NOT NULL
  ORDER BY m.created_at DESC LIMIT 1" > candidate.scad
openscad -o candidate.stl candidate.scad
```

Always take the LATEST code part (iterations append). Never trust the
in-browser preview as compile authority.

## The objective gate

Score the compiled STL (trimesh or makerbench-hwe's `mesh_objective_gate`
when available):

1. renders (compiles at all);
2. watertight;
3. nonzero volume;
4. fits envelope — compare **sorted** extents vs sorted envelope so
   orientation can't false-fail;
5. min wall ≥ the brief's floor;
6. body count ≥ the brief's min_bodies.

Report the sub-scores to the user in one line ("5/6 — min_wall misses on
the lattice"). Iterate in CADAM chat (user can take the keyboard — their
taste, their turns; re-extract from the DB after) until the gate passes or
the user accepts documented misses. Either outcome is a valid gate exit;
undocumented misses are not.

## Telemetry

OpenRouter cost: `GET https://openrouter.ai/api/v1/key` usage field,
delta before/after (lags a few minutes — snapshot early, read late).
Typical single-shot: $0.55–0.85, 2–4 min. Iterated session: a few dollars.
Record cost, wall time, and gate sub-scores for provenance.

## Alternate Stage 4 backend: live-CAD bridge (any agent model)

When the deliverable wants a real feature tree (native Fusion/SolidWorks
document, drawings later) instead of OpenSCAD, swap the CADAM lane for a
**live-CAD bridge** and keep everything else — the brief is still the
dimensional authority, the tournament winner is still the aesthetic
authority, and the same objective mesh gate scores the exported STL.

Reference implementation: **Luthier Bridge** (StudioPipeline-hwe) — loopback
HTTP on `127.0.0.1:8766` (`HWE_FUSION_PORT`), bearer token from the
`HWE_FUSION_TOKEN` user env var, two-phase **stage/confirm** on every
mutating operation. The Fusion add-in must be running (Utilities → Add-Ins →
LuthierBridge → Run; verify with `GET /ping`).

The driving agent is a free choice — the bridge doesn't care what model
pilots it. Claude drives it natively; a GPT-5.5 pilot works via
`codex exec` given (a) the bridge endpoint + token, (b) the design brief +
tournament synthesis, and (c) the instruction to stage operations and report
each staged batch for confirmation before committing. Stage/confirm is the
safety layer that makes third-party pilots acceptable in a live document:
nothing mutates until confirmed, and the session context is capturable for
provenance.

Export discipline (same as the Adam plugin lane): export STL/STEP yourself,
**verify millimetres** (SolidWorks paths default to inches; Fusion respects
document units), single-file STL for assemblies, then gate and ingest as a
distinct entrant (`luthier-bridge-<model>`) so pilots are comparable — same
tool, same brief, different pilot is a legitimate A/B axis.
