---
name: houseplant
description: Manage houseplant collection digital twins and care workflows. Use when working with houseplant or bonsai collection records, mobile photogrammetry or LiDAR scans, Blender MCP or bpy scene updates, annotated plant photos, bonsai pruning or wiring plans, bud or bloom tracking, care checklists, calendar reminders, propagation logs, or Obsidian/Markdown/spreadsheet plant databases.
---

# Houseplant

Use this skill to treat each houseplant as a living record plus a digital twin. Start with the user's collection database, update or simulate the plant's Blender state when available, then produce practical care outputs: annotated photos, decisive pruning or wiring plans with risk levels, calendar-ready follow-ups, and checklists.

## Core Workflow

1. Identify the plant record, specimen, and user goal. Prefer a stable `plant_id` from Obsidian, Markdown, or a spreadsheet; create a provisional id only when none exists.
2. Gather the minimum useful context: species or likely species, current date and location, indoor/outdoor placement, last water/fertilizer/repot/prune/wire events, health concerns, and the user's intended outcome.
3. Gather media and model inputs. For visual work, prefer front, back, left, right, top-down, trunk/root close-up, and target-branch close-up photos. For digital twins, also ask for or inspect `.blend`, `.obj`, `.ply`, `.glb`, texture, or scan folders.
4. Route to the right reference:
   - Blender or MCP digital twin work: read [`references/blender-digital-twin.md`](references/blender-digital-twin.md).
   - Bonsai pruning, wiring, aerial roots, or branch styling: read [`references/bonsai-module.md`](references/bonsai-module.md).
   - Obsidian/spreadsheet records, care checklists, or reminder drafts: read [`references/collection-records-and-care.md`](references/collection-records-and-care.md).
5. Make a decisive recommendation when the user asks for a plan. Include risk level, evidence, assumptions, and a quick pre-action verification step for irreversible physical actions.
6. Sync the result back to the user's chosen outputs: Blender scene changes, annotated images, plant record updates, calendar-ready reminders, and care checklists.

## Output Contracts

For a **Blender scene update**, report the scene file or target scene, changed collections or objects, assumptions about scale/orientation, simulation objects created, custom properties updated, exports produced, and unresolved uncertainties.

For a **bonsai pruning or wiring plan**, include branch ids or visual references, recommended action, reason, risk level, "verify before cutting/bending" check, aftercare, and follow-up date.

For **annotated photos**, use consistent color semantics: red for cut/remove, amber for watch/uncertain, blue for wire/bend, green for preserve/encourage, pink for bud/bloom event, and teal for aerial-root/root-work guidance. Keep labels short enough to remain readable on mobile.

For **calendar reminders**, provide exact dates or recurrence rules in plain language, the trigger evidence, priority, and a checklist. Create live calendar events only when the user asks and a calendar connector/tool is available; otherwise draft calendar-ready entries.

For **care checklists**, make them action-oriented and specimen-specific. Avoid generic "water every N days" rules unless the user explicitly wants a fixed cadence; prefer observation windows and tests such as soil moisture, pot weight, leaf turgor, growth stage, and recent weather.

## Decision Rules

- Prefer simulation before irreversible physical action. In Blender, create a separate simulation collection instead of overwriting the current-state twin.
- Preserve raw evidence. Do not destructively edit original scans, photos, or plant records; append dated logs and create derived artifacts.
- Be explicit about uncertainty. If species, scale, branch identity, seasonality, or health status is uncertain, state how that uncertainty affects the recommendation.
- Use risk levels:
  - `Low`: maintenance trimming, checklist updates, marker placement, reversible Blender-only changes.
  - `Medium`: structural pruning on a healthy plant, moderate wiring, care schedule changes after clear evidence.
  - `High`: major branch removal, trunk/root work, heavy bending, out-of-season interventions, weak or pest-stressed plants, or action based on poor media.
- Avoid restricted pesticide or hazardous treatment instructions. Prefer inspection, isolation, mechanical removal, cultural correction, and label-compliant local guidance.

## Skill Boundaries

This skill owns houseplant collection state, care workflows, Blender digital twins, and bonsai-oriented styling workflows. It may hand off to `reverse-engineer` when reconstructing a physical object or unknown mechanism from sparse photos, and to `makerspace` when the user wants fabrication plans for plant stands, jigs, fixtures, shelves, or watering hardware.

Do not turn every request into a full digital twin project. For a simple care question, use the collection record and produce a concise checklist. For a Blender request, assume Blender MCP is installed and operational, inspect the live scene before changing it, and leave the user with clear scene changes and next actions.
