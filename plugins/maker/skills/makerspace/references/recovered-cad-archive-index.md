# Recovered CAD Archive Index

Use this mini-pattern when a repo contains recovered CAD, mixed old/new
drawings, exported STLs/STEP/DXF, Illustrator/PDF layouts, screenshots, or
photos, and the first fabrication blocker is deciding what is actually
authoritative.

## When To Use

- A project repo has many CAD or drawing files but no current fabrication
  revision.
- File names imply versions such as `old`, `new`, `V1`, `V2`, `final`, or
  duplicate part names.
- Visual/layout files might be useful but lack units, scale, kerf, layer
  mapping, or drawing title-block review.
- A mechanism or furniture repo has enough design evidence to route, but not
  enough reviewed geometry to cut, print, or machine.

Do not use the index to certify a packet. It is a blocker list that tells the
next maker what must be reviewed before shop claims.

## Required Artifact

Create `cad-index.csv` before writing cut lists, CAM instructions, or
fabrication-ready drawing briefs.

Schema:

```csv
path,file_type,role,authority_status,revision_status,units_scale_status,stale_risk,next_review_action,notes
```

Recommended values:

- `authority_status`: `current`, `stale`, `visual_only`,
  `requires_export`, or `unknown`.
- `revision_status`: `reviewed`, `conflict`, `TBD`, or a named revision.
- `units_scale_status`: `checked`, `TBD`, or the known units plus a scale
  check.
- `stale_risk`: `none`, `possible`, `high`, or `TBD`.

Rows marked `unknown`, `visual_only`, `stale`, or `requires_export` must not
drive toolpaths, cut lists, or shop instructions until a design owner reviews
them.

## Minimum Readiness Gates

Add these gates to `validation.csv` or mirror them in the handoff:

| check_id | check_name | target |
| --- | --- | --- |
| CAD-IDX | CAD archive index | every candidate production file is indexed or explicitly excluded |
| CAD-AUTH | authority status | every file has an authority status and owner/reviewer action |
| CAD-UNITS | units and scale | every authority candidate has units, scale, origin/datum, and one known dimension checked or marked `TBD` |
| CAD-STALE | stale-file handling | duplicate, exported, old/new, and V1/V2 files are blocked from shop use until reviewed |
| CAD-EXPORT | fabrication export | CNC/laser/print routes name the export source and required metadata before CAM |

## Handoff Rule

Treat CAD, DXF/STEP, dimensioned drawings, measured templates, and reviewed
setup sheets as possible authority. Treat screenshots, generated images,
photos, README prose, chat summaries, and unlabeled Illustrator/PDF layouts
as support evidence until the index records scale, units, revision, and
operation meaning.

If mechanism intent or motion logic is missing, route to `reverse-engineer`
before making fabrication claims. `makerspace` can own the later BOM,
workholding, tolerance, safety, and machine-readiness gates once the geometry
and mechanism roles are understood.
