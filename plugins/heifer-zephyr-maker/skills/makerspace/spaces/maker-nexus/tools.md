# Tools — Maker Nexus, Sunnyvale CA

This is a starter document. Specific machines, models, and bed sizes
need verification against the Maker Nexus wiki and the actual shop
floor. The skill treats this as a snapshot, not gospel — when a real
build packet is being generated, the user should confirm any spec
that affects the build.

To populate this from the wiki, run:

```bash
python3 scripts/scrape_maker_nexus.py \
  --output ./spaces/maker-nexus/ \
  --merge
```

(Scraper currently a stub — see scripts/scrape_maker_nexus.py for
status.)

## Sections by area

### `#woodshop-area`

The woodshop is the largest tool area. Major machines (per
TBD-as-of-this-snapshot):

- Tablesaw
- Compound miter saw
- Jointer (8" or 12" — verify)
- Planer (15" or 20" — verify)
- Drum sander
- Bandsaws (1-2 of them — verify count)
- Drill press
- Router table
- Hand-tool benches with vises
- Shapers / spindle moulders if installed

Common consumables (member-supplied unless noted):
- Saw blades (tablesaw, miter, bandsaw)
- Router bits
- Drum-sander rolls
- Sandpaper

### `#cnc-area`

CNC router(s). Verify model and bed size on-site.
- Bed size: TBD
- Spindle: TBD HP
- Tool holder: TBD (likely ER-series)
- Vacuum table: TBD
- CAM software: Vectric VCarve, Fusion 360, or both — verify.

### `#laser-area`

Laser cutter(s). Verify model and wattage on-site.
- Bed size: TBD
- Wattage: TBD
- Type: CO₂
- Air assist: yes
- Fume extraction: yes (routed to roof)
- Auto-focus: TBD

### `#3d-print-fdm-area`

FDM printers. Number and model TBD. Common materials accepted:
PLA, PETG, ABS (with enclosure), TPU. Walk-in queue or reservation —
TBD.

### `#3d-print-resin-area`

Resin / SLA printers. Number and model TBD. Resin handling PPE
required (gloves, ventilation).

### `#metalshop-area`

Metalshop. Major machines TBD:
- Lathe(s)
- Mill(s)
- Welder(s) — MIG, TIG, stick — verify
- Plasma cutter — verify
- Sheet-metal brake / shear — verify
- Belt grinder
- Bandsaw (metal)

### `#textile-area`

Sewing and textile area:
- Sewing machines (domestic and/or industrial — verify)
- Sergers
- Embroidery machines
- Pressing tools
- Cutting mats

### `#electronics-bench`

Open electronics bench:
- Soldering stations
- Hot-air rework
- Microscope (TBD)
- Power supplies
- Oscilloscope (TBD bandwidth)

## Hand-curated additions

(This section is preserved when the scraper runs. Add anything not
on the wiki here.)

- TBD
