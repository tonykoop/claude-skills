# Domain-Label Auto-Routing

Story #242. A data-driven ruleset that maps capture keywords/signals to domain
labels for HWE/maker captures, with confidence thresholds and a
fallback/needs-triage path. Keep this table the source of truth so routing is
easy to extend without touching code.

Used by the parser (Stage 3 of the
[Gemini export pipeline](gemini-export-pipeline.md)) and mirrored in the inline
fallback inside [`../scripts/gemini_to_github.py`](../scripts/gemini_to_github.py).
It also produces the tags the [institutional-knowledge pre-read](institutional-knowledge.md)
filters on, so keep the label vocabulary aligned with
[`label-schema.md`](label-schema.md).

## How routing works

1. Lowercase the capture text (title + body).
2. For each domain, count keyword/signal hits and sum their weights.
3. Assign every domain whose score meets the **promote threshold**.
4. If no domain meets the **triage threshold**, route to `needs-clarification`
   (the fallback path). Never silently drop to `general` for HWE/maker captures
   - an unroutable hardware idea is a triage signal, not a generic one.
5. `capture` is always added.

### Confidence thresholds

| Outcome | Rule |
|---|---|
| **Confident** | score >= 2 weighted hits, OR one strong (weight-3) signal. Apply the domain label. |
| **Tentative** | score == 1 weak hit. Apply the domain label AND `needs-clarification`. |
| **Unroutable** | score == 0 across all domains. Apply `needs-clarification` only. |
| **Multi-domain** | more than one domain confident -> apply all; also add `maker` if any HW domain fired (hybrid signal). |

Weights: a generic keyword = 1, a strong/unambiguous signal = 3. Strong signals
are marked **(3)** in the table below.

## Routing table

| Domain label | Keywords / signals |
|---|---|
| `instrument` | flute, didgeridoo, harp, drum **(3)**, reed, fipple, bore, tuning, acoustic, soundboard, string tension |
| `woodworking` | wood, plywood, hardwood, joinery **(3)**, dovetail, lathe, router table, cabinet, glue-up, grain |
| `sheet-metal` | sheet metal **(3)**, brake, bend allowance **(3)**, flat pattern **(3)**, plasma, shear, slip-roll, weld, gauge |
| `electronics` | pcb **(3)**, pcba **(3)**, schematic, gerber, microcontroller **(3)**, mcu, sensor, i2c, spi, voltage, circuit |
| `firmware` | firmware **(3)**, flash, bootloader, rtos, embedded, register, interrupt, hal |
| `software` | app, api, webhook **(3)**, script, cli, automation, database, frontend, backend, service |
| `yoga` | yoga **(3)**, vinyasa **(3)**, asana, pose, sequence, peak pose, savasana |
| `maker` | jig, fixture, workholding, mold, cnc, laser cutter, 3d print, mill, fabricate |

Notes:
- `firmware` and `electronics` frequently co-fire; that is the hybrid case the
  [hybrid issue template](templates/hybrid-issue-template.md) exists for.
- When any of `instrument`, `woodworking`, `sheet-metal`, `electronics`,
  `firmware`, or `maker` fire, also add `maker` as the umbrella domain so
  shop-floor captures stay groupable.

## Fallback / needs-triage path

An unroutable or tentative capture is not a failure - it is a request for one
clarifying detail. The parser should:

1. Apply `needs-clarification`.
2. Surface the single missing signal that would route it ("is this HW, SW, or
   both?").
3. Leave the issue open and visible in Review mode rather than guessing.

## Extending the table

- Add a row or a keyword; do not encode routing logic in scripts.
- Keep label names in lockstep with [`label-schema.md`](label-schema.md). If a
  new domain is added here, add it there too (and to the bootstrap label list).
- Prefer a few strong **(3)** signals over many weak keywords - precision beats
  recall for triage, because a wrong confident label is costlier than a triage
  flag.
- When the routing vocabulary changes, re-check the inline fallback in
  `gemini_to_github.py` so the script and this table do not drift.
