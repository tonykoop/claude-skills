# Logistical Breakdown Pass — Reference

The logistical breakdown converts the script into a production-ready segment table. Every row corresponds to one distinct segment — a camera position, an asset to produce, a line to record, or an on-screen graphic to design. The breakdown is what a 1st AD (first assistant director) would use to schedule shoot days and what a producer would use to flag missing assets before principal photography.

## Segment types

| Code | Type | Description |
|------|------|-------------|
| `A` | A-roll | Primary footage: presenter on camera, interview, direct-to-camera narration |
| `B` | B-roll | Secondary footage: establishing shots, action cutaways, reaction shots |
| `GEN` | Generated | AI-generated images or video (Midjourney, Sora, Runway, etc.) |
| `TEXT` | On-screen text | Lower-thirds, title cards, callouts, captions |
| `MUSIC` | Music | Background score segment — note mood, energy level, approximate runtime |
| `SFX` | Sound effect | Non-music audio: ambient sound, transition whoosh, notification tone |
| `VO` | Voiceover | Off-camera narration over B-roll or visuals (distinct from A-roll if speaker not on camera) |

## Breakdown table format

One row per segment:

| # | TC-in | TC-out | Dur | Type | Description | Assets needed | Props / wardrobe | Location | Missing / at risk |
|---|-------|--------|-----|------|-------------|---------------|-----------------|----------|-------------------|

Field definitions:
- **TC-in / TC-out**: timecode or script cue label (e.g. `0:00`, `Hook`, `CTA`)
- **Dur**: approximate duration in seconds
- **Type**: segment type code from the table above
- **Description**: one sentence describing what appears on screen and what is said
- **Assets needed**: list of specific files, shots, or generated images required
- **Props / wardrobe**: physical items needed in frame (if A-roll)
- **Location**: shoot location or `POST` (post-production) or `GENERATED`
- **Missing / at risk**: blank if all assets exist; `WARN` if asset must be created; `BLOCK` if asset is required and no path to production is known

## Procedure

1. Read the script from top to bottom, splitting it at every change of:
   - Camera angle or shot type
   - Segment type (A-roll to B-roll, narration to text card, etc.)
   - Scene location
   - Named asset (e.g. "cut to the bench" → new row)

2. Assign TC-in and TC-out from the script's timing markers if present; otherwise estimate from word count (average 2.5 words/second for narration, 1.5 words/second for yoga).

3. Flag every segment that requires an asset not yet in the project folder as `WARN`. Flag segments with no known path to producing the asset as `BLOCK`.

4. Output the table using `scripts/breakdown_parser.py` if the input script is in Markdown with `[TC]` annotations; otherwise produce the table manually.

## Common patterns by channel archetype

| Archetype | Typical segment mix |
|-----------|---------------------|
| yoga | A-roll (instructor) + B-roll (students) + GEN (opening/closing image) + TEXT (CTA) |
| instrument-maker | A-roll (build steps) + B-roll (close-ups) + TEXT (spec callouts) + VO (narration) |
| AI/agentic | A-roll (demo) + TEXT (code snippets) + GEN (concept visuals) + MUSIC (background) |
| consciousness | VO (reflective narration) + GEN (abstract visuals) + MUSIC + TEXT (quotes) |
| WRFcoin | A-roll (explainer) + TEXT (data labels) + B-roll (charts/graphs) + MUSIC |

## Missing-asset escalation

Segments marked `BLOCK` must appear in the greenlight verdict as BLOCKER-level issues. Segments marked `WARN` appear as POLISH issues unless they are required for the core story (in which case: BLOCKER).
