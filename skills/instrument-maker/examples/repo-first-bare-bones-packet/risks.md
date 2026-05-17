# Risks

## Acoustic Model Risk

- Risk: The governing acoustic model is still unknown or unmeasured.
- Impact: CAD dimensions may tune incorrectly.
- Mitigation: Mark affected dimensions as `measurement-required`; run the
  relevant validator once a structured spec exists.

## Fabrication Authority Risk

- Risk: The repo has sketches or concept images before CAD/DXF authority.
- Impact: A reader may treat non-dimensional imagery as cut-ready geometry.
- Mitigation: Keep `drawing-brief.md` explicit about which future file becomes
  fabrication authority.

## Sourcing Risk

- Risk: Supplier listings, prices, or part dimensions drift.
- Impact: BOM becomes misleading.
- Mitigation: Use `source_status` fields and verify current facts before any
  purchase recommendation.

## Privacy Risk

- Risk: Story, photos, or location notes accidentally expose private details.
- Impact: Public repo becomes hard to share safely.
- Mitigation: Keep photo and story prompts generic until publish review.

## Scope Risk

- Risk: Bare-bones packet gets mistaken for a full v4 build packet.
- Impact: Missing validation, drawings, or tests are overlooked.
- Mitigation: Keep status language in README and design notes until promotion
  gates pass.
