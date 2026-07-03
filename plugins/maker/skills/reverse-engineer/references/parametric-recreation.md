# Parametric Recreation Branch (image → executable CAD)

Proven 2026-07-02 on a four-instrument pilot series (sambuca from a museum
photo, Luthieros-style 13-string lyre, fujara, portative organ): the skill's
photo-intake discipline can end in an **executable parametric recreation** —
BOSL2/OpenSCAD source with named per-part modules and editable parameters —
not just RE notes. The fujara recreation scored a perfect 1.000 on an
objective mesh gate with a spec-exact 1551mm bore. Typical cost was
$0.55–0.85 and 2–4 minutes per single-shot generation with Claude Fable 5.

## When to branch here

Enter this branch only after the normal observation ledger exists (claims
labeled, confidence attached). The recreation prompt is *built from* the
ledger — this branch converts disciplined RE notes into CAD, it does not
replace the discipline. If `image_access_mode` is degraded, the recreation
inherits `provisional` status automatically.

Requirements:

- An image-conditioned code-CAD tool. Reference setup: a local CADAM
  instance (github.com/Adam-CAD/CADAM, GPLv3) with a Claude model as engine
  via OpenRouter. Tony's lives at `_meta/CADAM` (login + notes in
  `_meta/cadam-notes.md`, one-shot env setup in `_meta/cadam-setup.sh`).
  Any equivalent image+text → OpenSCAD flow works.
- Local OpenSCAD with the BOSL2 library installed. Both sides on WSL
  machines: `~/.local/share/OpenSCAD/libraries/BOSL2` (Linux) and
  `Documents\OpenSCAD\libraries\BOSL2` (Windows).
- Optional but recommended: an objective mesh gate for validation
  (makerbench-hwe's `mesh_objective_gate`: renders / watertight /
  nonzero_volume / fits_envelope / min_wall / body_count).

## Prompt recipe (the load-bearing part)

Write the generation prompt exactly like a benchmark task brief. Distill
the observation ledger into it:

1. **Attach the source photo** and say what role it plays: "Use the attached
   photo as visual inspiration" (aesthetic target) vs "recreate this object"
   (fidelity target). Confidence-marked dims from the ledger become stated
   numbers; `unknown`s become explicitly-named parameters with placeholder
   defaults.
2. **One self-contained program.** Demand the complete OpenSCAD program in
   one block, with BOSL2 allowed.
3. **Named module per part + top-level assembly**, parts as *distinct
   bodies* ("do not fuse across the joint"). This is what makes the result
   editable and lets body-count validation work.
4. **Editable parameters**: name every parameter you want exposed, with the
   ledger value in parentheses — `body_length_mm (336)`. These become
   Customizer sliders.
5. **State fabrication floors in the prompt**: minimum wall thickness ("every
   solid wall ≥ 2mm; no decorative sub-millimeter features"), overall
   envelope. Un-stated floors are the #1 gate failure: display strings,
   cutout edges, and decorative features routinely come back sub-millimeter.
6. **State placeholders for measurement-gated features** ("the flue pattern
   is a placeholder; real geometry requires measurement") so the recreation
   never launders an `unknown` into apparent fact.
7. **Cap tessellation**: "keep $fn moderate (≤96) so the model compiles
   quickly." Dimpled/domed compound surfaces at high $fn can take 10+ minutes
   in OpenSCAD; a render-budget blowup looks like a failure but is actually a
   cost problem.

## Extraction and export

- In CADAM, submit with **Enter in the textarea** — the sparkle button is a
  prompt *enhancer*, not submit.
- The SCAD source of truth lives in CADAM's local Supabase, not the DOM:

  ```sql
  SELECT part->'input'->>'code'
  FROM public.messages m, jsonb_array_elements(m.parts) part
  WHERE m.conversation_id = '<conv-id>'
    AND part->'input'->>'code' IS NOT NULL
  ORDER BY m.created_at DESC LIMIT 1;
  ```

  (via `docker exec supabase_db_cadam psql -U postgres -d postgres -t -A -c ...`).
  DB extraction beats DOM scraping every time; the UI truncates.
- Compile locally (`openscad -o candidate.stl candidate.scad`) rather than
  trusting the in-browser preview; the browser renderer accepts geometry
  the CLI rejects.

## Validation

Gate the compiled STL before presenting it as a recreation:

- renders, watertight, nonzero volume;
- fits the envelope from the ledger (compare **sorted** extents so a
  lying-down model isn't falsely failed);
- min-wall ≥ the floor you stated in the prompt;
- body count ≥ the number of distinct parts the ledger identified.

Known failure signature: **min_wall is the universal image-tier miss** —
the model adds thin display geometry (strings, lattices, decorative edges)
that fails fabrication floors while looking great. Fix by exporting a *gate
variant* with decorative bodies disabled (a `show_display_geometry = false`
parameter), or by iterating with the floor restated.

## Provenance discipline (non-negotiable)

Every recreation artifact gets a provenance record next to it:

- pipeline (tool, model, e.g. "CADAM + claude-fable-5 via OpenRouter");
- source image path + `image_access_mode` from the ledger;
- wall time, thinking time if visible, and **API cost** (for OpenRouter:
  usage delta from `GET /api/v1/key` before/after — note it lags a few
  minutes);
- gate sub-scores;
- the label **GENERATED — not a measured master**. A recreation never
  silently becomes reference geometry; it stays provisional until the
  builder-ready gate of the main skill passes with real measurements.

## Iteration loop

The human iterates in the tool's chat with the model (the lyre pilot took
three user iterations to a thigh-cradle redesign, ~$4 total). Re-extract
from the DB after each round — take the **latest** code part. Track cost
per session, not per message.
