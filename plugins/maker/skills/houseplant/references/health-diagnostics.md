# Computer-Vision Plant Health Diagnostics

Read this reference when the user uploads photos and you can run an optional **health pass** — a "check-engine light" for the plant. It reuses the multi-angle photo set the skill already collects for pruning/capture (see [`capture-pipeline.md`](capture-pipeline.md)), so there is **no extra capture burden**. It cross-references findings against recent care events from [`collection-records-and-care.md`](collection-records-and-care.md) and escalates the risk level of any pruning/wiring action via [`bonsai-module.md`](bonsai-module.md).

## Posture: inspection, not diagnosis or treatment

This is a screening tool, not a diagnosis. It **flags** anomalies and tells the user where and what to inspect. It does not prescribe chemical treatments. Favor, in order: **inspection -> isolation -> mechanical removal -> cultural correction**, and defer to label-compliant local guidance for any chemical. Always state uncertainty.

## When to run it

- Run automatically as a low-key pass whenever the user uploads plant photos for any reason ("I also did a quick health check on these photos: ..."), unless they decline.
- Run explicitly when the user says the plant looks off, is yellowing, dropping leaves, sticky, spotted, or has visible bugs/webbing.

## What the vision pass looks for

Scan each photo (and compare across angles and across time if prior photos exist) for:

**Color / chlorosis patterns**
- Uniform yellowing of older (lower) leaves -> often nitrogen/light or natural senescence; cross-check fertilizer + light.
- Interveinal yellowing (green veins, yellow between) -> micronutrient/iron, often pH or waterlogging linked.
- Yellowing + leaf drop concentrated after a move/repot -> stress/shock, cross-check `repotted`/relocation events.
- Brown crispy leaf margins/tips -> underwatering, low humidity, salt buildup, or fertilizer burn.
- Soft, dark, mushy leaves/stems or yellowing from the base up -> overwatering/root-rot risk; cross-check watering cadence and drainage.

**Leaf-drop pattern**
- Sudden whole-plant drop vs. gradual oldest-first vs. one-side-only (light/draft). The *pattern* is the clue — record which.

**Common indoor pests (flag the visual signature; recommend inspection, not pesticide)**
- **Spider mites** — fine webbing in leaf axils, stippled/speckled pale leaves, dusty underside. Common on stressed ficus in dry heat.
- **Scale** — small brown/tan immobile bumps along stems and leaf veins; sticky honeydew; sooty mold.
- **Mealybugs** — white cottony tufts in crotches and leaf joints.
- **Thrips** — silvery streaking/scarring, tiny black frass specks, distorted new growth.
- **Fungus gnats** — small flies around soil -> usually a wet-substrate symptom, cultural correction (let dry, bottom-water).

Be conservative: a brown spot can be many things. Flag the *candidate* and the *region*, and ask for a closer macro shot before naming a pest with confidence.

## Cross-reference the care record

A visual flag is far more useful in context. Before concluding, pull recent events from the plant timeline:

- Recent `repotted` / relocation -> favor shock over disease for sudden drop.
- Watering cadence (from `chrono-engine.md` / log) -> distinguishes under- vs. over-watering chlorosis.
- Recent `fertilized` -> margin burn vs. deficiency.
- Existing `health_flags` -> is this new, worsening, or resolving?

State the cross-reference in the output ("yellowing of lower leaves + a repot 9 days ago -> most likely transplant stress, not deficiency").

## Output: health flags on the record

The vision pass names the symptoms; [`../scripts/health_triage.py`](../scripts/health_triage.py)
turns them into the records below deterministically — it maps each symptom to a
candidate flag, cross-references recent care events (a repot within ~14 days
re-reads a sudden drop as stress; a recent feed re-reads margin burn as
fertilizer/salt), defaults pest/rot candidates to **low** confidence, and emits
the `health_flag_added` blocks plus the structural-risk verdict. Feed it the
observed symptoms as JSON (`{"observations": [...], "care_events": [...],
"today": "..."}`); it never recommends a chemical.

Each finding becomes a `health_flag_added` event (existing event type) with evidence:

```markdown
### <YYYY-MM-DD> — health_flag_added
- Flag: <chlorosis-lower-leaves | webbing-suspected-spidermite | scale-suspected | leaf-margin-burn | rot-risk>
- Evidence: photo <filename>, region <e.g. lower-left interior leaves>
- Cross-ref: <recent care events that support/contradict>
- Confidence: <low | medium | high>
- Recommended next step (inspection-first): <isolate | macro photo | check undersides | check soil/roots | cultural correction>
- Chemicals: none recommended here; if needed, follow label-compliant local guidance.
```

When the issue improves, log `health_flag_resolved`.

## Risk escalation into pruning/wiring

Any **open** health flag should escalate the risk of structural work, per `bonsai-module.md`:

- A plant with an active pest or rot flag is by default **not** a candidate for structural pruning, wiring, root work, or aerial-root guidance — those become **High** risk.
- Downgrade to maintenance-only (remove obviously dead material, improve culture, isolate) until the flag is resolved.
- Surface this in any pruning/wiring/aerial-root plan: "Risk raised to High: open `webbing-suspected-spidermite` flag from 2026-06-15. Recommend resolving before structural work."

## Decision rules

- Screen, don't diagnose. Name candidates with explicit confidence; request a closer photo before committing.
- Inspection / isolation / mechanical removal / cultural correction over chemicals, always.
- No restricted-pesticide or hazardous-treatment instructions; defer to label-compliant local guidance.
- Preserve evidence: reference the original photo filenames; never edit originals.
