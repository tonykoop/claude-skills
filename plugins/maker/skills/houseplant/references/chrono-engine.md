# Chrono-Horticultural Engine

Read this reference when the user asks about care scheduling, watering/fertilizing windows, or wire-removal checks. This module produces dynamic, observation-driven reminders instead of fixed timers.

## Core Workflow

1. **Ingest Context:** 
   - Species profile (e.g. cambium thickening rate, water needs).
   - Current date and season.
   - Placement: indoor vs. outdoor.
   - Recent stressors (repot, hard prune, pest treatment).
   - Local climate signal (if available, e.g. "hot balcony weather").
2. **Determine Care Windows:**
   - **Watering/Fertilizing:** Compute frequency checks based on the above variables.
   - **Wire Removal:** Auto-schedule wire-removal inspection windows based on the date the wire was applied and the species-specific cambium thickening rate.
3. **Emit Calendar-Ready Reminders:**
   - Output must be phrased as **checks** (e.g., "Check soil moisture every 2 days during hot balcony weather") rather than fixed actions ("Water every 2 days").
   - Include wire-bite-in inspection windows.
4. **Log the Event:** Use the formats defined in `collection-records-and-care.md` to record the scheduling event and link it to the plant's record.

## Wire-Removal Inspection

Use the bundled `scripts/wire_window.py` to estimate the first inspection date.

1. Note the `applied_date` and the `species`.
2. Determine the relative growth rate (fast, medium, slow).
3. The script provides the initial inspection cadence (e.g., 4 weeks for fast-growing species during active growth).

## Out of Scope

- **Live Calendar Event Creation:** Do not attempt to push events directly to the user's calendar unless explicitly requested and a suitable calendar connector tool is available.
- **Pesticide/Treatment Recommendations:** Handled separately. Only provide label-compliant guidance.

## V2 Data-Model Schema Extensions

This module extends the V1 minimal plant record defined in `collection-records-and-care.md` with:

```markdown
---
# ... existing frontmatter ...
chrono_active_windows:
  - type: wire_inspection
    start_date: YYYY-MM-DD
    frequency_days: 14
    trigger: applied_date (YYYY-MM-DD)
  - type: watering_check
    frequency_days: 2
    condition: "hot balcony weather"
---
```

Use these properties to track active dynamic windows in the canonical record.
