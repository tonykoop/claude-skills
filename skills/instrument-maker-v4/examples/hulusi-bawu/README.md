# Hulusi / Bawu Readiness-Gated Example

This example is a stopped-pipe free-reed validation scaffold. It is not a
build-ready packet.

Use it when an existing hulusi or bawu repo has enough packet structure to
name the reed, pipe, workbook, drawing, or validation artifact under test, but
does not yet have HUL-P0 reed coupon and HUL-P1 single-pipe measurements.

Files:

- `family-spec.csv` keeps the acoustic law at
  `unknown_requires_measurement` until measured evidence exists.
- `validation-loop.csv` shows the minimum empirical checks for HUL-P0 and
  HUL-P1.
- `visual-output-register.csv` marks the design table as fabrication
  authority and concept imagery as non-authoritative.

Do not promote this scaffold to family-ready CAD/DXF until the measured rows
support that claim.
