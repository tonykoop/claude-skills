# Presentation And Print Packets

Use this reference when the user wants the project explained to collaborators, shop users, makerspace staff, customers, grant reviewers, or future Tony away from the keyboard.

## Capstone Slide Deck (.pptx)

Create a capstone slide deck after the build packet has meaningful content. It should be the orientation layer for the whole project, not another pile of data.

### Recommended slide flow

1. **Title** — instrument name, build ID, hero image/render.
2. **What this project is** — one-sentence concept and intended use.
3. **File map** — every major file, what it does, how to use it.
4. **Build workflow** — design → source → cut → fixture → assemble → tune → validate.
5. **Design sheet** — key inputs, formulas, assumptions, links.
6. **BOM and sourcing** — material/hardware summary, cost status, supplier status.
7. **Drawings, CAD, CNC** — what exists, what is placeholder, where to find it.
8. **Visual BOM / product sketch** — image-forward resource view.
9. **Assembly and shop use** — what to print or take to the makerspace.
10. **Validation** — tuning targets, measurement plan, pass/fail checks.
11. **Open risks / decisions**.
12. **Next actions**.

### Deck quality rules

- Each slide answers one practical question.
- Prefer screenshots, file previews, renders, diagrams over dense bullets.
- Put file links directly on slides when possible.
- Label generated/concept images as placeholders.
- Add speaker notes for operational details that would clutter the slide.
- Keep typography large enough for a room, not just a laptop.
- Use consistent section colors: design, sourcing, shop, validation, presentation.

## Printable Shop Packet (.pdf)

Create a single print-friendly packet after all edits are done. It should combine the useful Markdown/CSV content into one document a user can take shopping or into the shop.

### Recommended order

1. Cover / project summary.
2. Quick start and file map.
3. Design intent and assumptions.
4. BOM.
5. Sourcing list.
6. Cut list and stock/yield.
7. Drawing brief and critical dimensions.
8. Assembly manual.
9. Validation/tuning sheet.
10. Supplier RFQ.
11. Visual BOM brief.
12. Appendix: raw formulas, manifest, links.

### Print quality rules

- Include page breaks between major sections.
- Make tables readable in portrait or landscape; split wide tables if needed.
- Include checkboxes/blanks for shop notes and measured values.
- Include absolute local paths and relative packet paths.
- Prefer black text on white, no dark backgrounds.
- Preserve source filenames so printed pages map back to files.

## Automation

Use `scripts/generate_capstone_docs.py` from a generated build packet folder.

```bash
python3 scripts/generate_capstone_docs.py /path/to/build-packet --title "Tongue Drum Capstone"
```

The script writes:

- `capstone-deck.md` — slide outline (always).
- `capstone-deck.pptx` — slide deck (when `python-pptx` is installed; included in Cowork).
- `print-packet.md` — combined Markdown packet (always).
- `print-packet.html` — print-ready HTML with page breaks and CSS (always).
- `print-packet.pdf` — print-ready PDF (when `reportlab` is installed; included in Cowork).
- `capstone-manifest.json` — manifest of all outputs.

## Cowork-Specific Production Notes

In Cowork mode, Claude has access to:

- `python-pptx` — programmatic .pptx generation.
- `reportlab` — programmatic .pdf generation.
- `openpyxl` — programmatic .xlsx editing.
- `python-docx` — programmatic .docx generation.

This means the capstone deck and printable packet can be produced as real binary deliverables, not just markdown drafts. The hand-off to a recruiter/collaborator should include `capstone-deck.pptx` and `print-packet.pdf` (or compiled docx) — not the raw Markdown.

When Google Slides or Microsoft 365 connectors are available in chat, the deck can also be uploaded after local files are generated.

## Related Skills

- `pptx` skill — use when fine control of slide layouts, themes, charts, or images is needed beyond what `generate_capstone_docs.py` produces.
- `pdf` skill — use when more sophisticated PDF layout, form fields, or table-heavy formatting is needed.
- `docx` skill — use when Tony wants the print packet as a Word document instead of PDF.
