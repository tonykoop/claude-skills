# Design Notes

## Project Identity

- Project name: TBD
- Instrument family: TBD
- Intended build method: TBD
- Current status: bare-bones readiness packet
- Build readiness: not build-ready

## Design Intent

Describe the musical goal, target player/use, rough size class, and why this
instrument belongs in its own repo. Keep this section public-safe and avoid
private family/media details.

## Known Inputs

| Input | Value | Provenance | Status |
| --- | --- | --- | --- |
| Target pitch/range | TBD | TBD | measurement-required |
| Material family | TBD | TBD | assumption |
| Fabrication process | TBD | TBD | assumption |
| Reference instrument or precedent | TBD | TBD | unverified |

## Open Measurements

| Measurement | Why it matters | Owner/source | Status |
| --- | --- | --- | --- |
| Critical acoustic dimension | Tunes the instrument or validates model choice. | TBD | measurement-required |
| Critical fit/clearance | Controls assembly and serviceability. | TBD | measurement-required |
| Critical structural dimension | Controls safe handling or toolpath feasibility. | TBD | measurement-required |

## Authority Notes

- CAD/DXF is future fabrication authority unless measured geometry already
  exists and is named here.
- Generated images may support mood, concept, or presentation only.
- Supplier listings are not stable design data until checked for this request.

## Promotion Notes

Promote this repo to a full packet only after the validation gates in
`validation.csv` have a pass path and each `measurement-required` field above
has either a value or an explicit experiment plan.
