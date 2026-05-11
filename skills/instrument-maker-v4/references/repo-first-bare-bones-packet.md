# Repo-First Bare-Bones Packet Template

Use this reference when an instrument repo or issue is labeled
`readiness:bare-bones`, asks for a "first packet", or needs a public repo
starting point before enough measurements exist for a full v4 packet.

This is a readiness template. It creates a clean repo-root scaffold and makes
unknowns visible. It is not a build-ready packet, CAD release, supplier quote,
or measured acoustic design.

## When To Use

Use this path when:

- The output is a standalone instrument repo, not a multi-packet workspace.
- The user wants a small first pass that can be reviewed, versioned, and
  expanded later.
- Instrument family, materials, rough build method, or story intent is known,
  but measured geometry, CAD/DXF, or tuning data is not complete.
- The next useful step is to define decisions and evidence gaps rather than
  claiming fabrication readiness.

Do not use this path when the user explicitly asks for a complete build packet
from a populated catalog row. Use the full Mode A or Mode B packet workflow in
the canonical skill instead.

Do not use this path when an existing prototype repo already has packet
artifacts and needs measurement history, iteration decisions, or empirical
cleanup. That is a validation-loop upgrade, not a fresh bare-bones starter.

## Output Shape

Create files at the repository root:

| File | Required content |
| --- | --- |
| `README.md` | Project summary, current status, file map, next gates, and license note. |
| `design.md` | Intent, assumptions, open measurements, design decisions, and non-authority warning. |
| `bom.csv` | Starter materials/components with `status` and `source_status` fields. |
| `sourcing.csv` | Vendor/search/provenance placeholders without time-sensitive purchase claims. |
| `cut-list.csv` | Candidate parts or coupons with `TBD` dimensions where geometry is not authoritative. |
| `validation.csv` | Gates, next actions, and evidence needed before full packet/CAD readiness. |
| `risks.md` | Failure modes and mitigations for acoustics, fabrication, safety, and scope. |
| `drawing-brief.md` | Required future drawings, authority level, and what each drawing must prove. |
| `photo-shotlist.md` | Optional public-safe documentation shots; no private family/media assumptions. |

Optional folders may be created later (`drawings/`, `cad/`, `images/`,
`data/`, `site/`), but the bare-bones template should not add empty folders
unless the repo already has a convention for them.

## Required Status Language

Every bare-bones packet must state:

- Current status: `bare-bones readiness packet`.
- Fabrication authority: `not build-ready`.
- CAD/DXF status: `future authority unless measured geometry already exists`.
- Sourcing status: `unverified until checked at purchase time`.
- Measurement status: `TBD` or `measurement-required` for dimensions that
  affect tuning, fit, machining, structural safety, or ergonomics.

Use `TBD`, `assumption`, `derived estimate`, or `measurement-required` in the
file where the unknown appears. Do not hide unknowns in prose.

Use `next_action` and `evidence` in validation rows so the next builder can see
what to do and where the claim came from.

## Hard Boundaries

- Do not publish private family, child, location, or media details.
- Do not use generated images as dimensional or fabrication authority.
- Do not claim a price, lead time, machine setting, or supplier availability is
  current unless it was verified for this request.
- Do not imply a full instrument family is ready when only a coupon, mockup, or
  design sketch exists.
- Do not nest this packet under `build-packets/`; this template is repo-first.

## Promotion Gates

Move from bare-bones to a full packet only when:

- Open measurements in `design.md` have owners or recorded values.
- `validation.csv` has a pass path for acoustics/tuning, fabrication, safety,
  and documentation.
- The drawing brief identifies which file becomes fabrication authority.
- BOM and sourcing rows distinguish in-hand, verified, supplier-unverified, and
  substitution-candidate parts.
- Risks that could change the core architecture have a mitigation or a planned
  test.

For wind or free-reed instruments, run `scripts/validate_acoustic_law.py` when
`family-spec.csv` exists. Until then, mark the acoustic model as
`measurement-required` in the design notes.

## String / Spike-Fiddle Variant

Use this variant for huqin-family starters such as erhu when the repo is still
bare-bones and the next useful step is to expose setup and drawing unknowns.
This is still a repo-first readiness packet, not a build-ready spike-fiddle
plan.

Required guardrails:

- Treat active string length as the qianjin-to-bridge speaking span, not total
  string length.
- Record `380-420 mm` only as a first-pass setup range for erhu-like starters,
  with status `measurement-required` or `assumption` until selected or
  measured.
- Require separate measurement gates for bridge placement, qianjin
  placement/height, neck/spike alignment, peg/string path, resonator/body
  envelope, and membrane/soundboard interface.
- Treat an `artifact:dxf` routing label as a future authority preference, not
  permission to invent cut-ready geometry.
- Keep concept images, SVG previews, drawing PDFs, and render previews out of
  the fabrication authority chain unless they are derived from named DXF/CAD,
  design-table, measured-template, or reviewed-drawing authority.

For a compact starter example, see
`examples/repo-first-bare-bones-packet/string-spike-fiddle/`.
