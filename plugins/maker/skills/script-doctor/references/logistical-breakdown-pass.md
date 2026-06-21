# Logistical Breakdown Pass Reference

Parse the script into a production asset table. One row per ~60-second segment or distinct content block.

## Segment types

| Type | Definition |
|---|---|
| `A-roll` | On-camera talent / interview / presenter |
| `B-roll` | Cutaway footage — must be sourced or shot separately |
| `GEN` | AI-generated image or video (agy, Firefly, Sora, etc.) |
| `TEXT` | On-screen graphic, caption, lower third |
| `MUSIC` | Background track, sting, or sound design |
| `SFX` | Spot sound effect (not background music) |
| `ANIM` | Motion graphic or animation |

## Breakdown table schema

| TC-in | TC-out | Type | Description | Assets needed | Props | Location | Missing / at risk |
|-------|--------|------|-------------|---------------|-------|----------|-------------------|

- **TC-in / TC-out**: timecode or segment label (e.g. "0:00", "Hook", "Act 2 open")
- **Description**: one-line shot or content description
- **Assets needed**: filenames, footage slugs, graphic titles, music track names
- **Props**: physical objects required on set (instruments, tools, hardware, food, etc.)
- **Location**: studio / home shop / outdoor / stock footage / archival
- **Missing / at risk**: any asset not yet created, sourced, or confirmed available

## Flagging conventions

Prefix with severity in the **Missing / at risk** column:

- `BLOCKER:` — production cannot proceed without this
- `RISK:` — can proceed with a workaround, but quality suffers
- `NOTE:` — plan ahead, not immediately blocking

## A-roll blocking

For each A-roll segment note:
- Teleprompter or memorized?
- Single-take or multiple setups?
- Any costume / background / lighting changes?

## Stock and archive

For B-roll sourced from stock or archive, note:
- Preferred library (Artlist, Storyblocks, Pixabay, etc.)
- Search keywords
- License needed (commercial / editorial / free)

## AI-gen segments

For GEN segments:
- Note which tool (agy, Firefly, Sora, Kling, etc.)
- Paste the intended prompt or describe the visual
- Flag if the tool's output style must match a previously generated asset (consistency risk)

## Output format

Emit the breakdown as a Markdown table, then a **Missing assets summary** section:

```
## Logistical Breakdown

| TC-in | TC-out | Type | Description | Assets needed | Props | Location | Missing / at risk |
|-------|--------|------|-------------|---------------|-------|----------|-------------------|
...

## Missing assets summary

BLOCKER
  - [asset] ([TC]) — [why blocking]

RISK
  - [asset] ([TC]) — [mitigation option]

NOTE
  - [asset] ([TC]) — [action]
```
