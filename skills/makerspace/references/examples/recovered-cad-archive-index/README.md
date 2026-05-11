# Recovered CAD Archive Index Example

This tiny example demonstrates `cad-index.csv` for a recovered furniture or
mechanism archive. It is not a build packet and does not certify any file for
fabrication.

Use this shape when a repo has SolidWorks, STEP/DXF/STL exports, PDF/AI
layouts, screenshots, or drawings whose revision authority is unclear.

Validation:

```bash
python3 skills/makerspace/scripts/validate_packet.py --schemas-only \
  --packet skills/makerspace/references/examples/recovered-cad-archive-index
```
