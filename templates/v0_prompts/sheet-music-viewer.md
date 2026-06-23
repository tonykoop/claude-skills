# Template: Sheet-Music Viewer

**Target platform:** v0.dev (primary) · Replit Agent (also works)  
**Story:** #487  
**Date:** 2026-06-22

---

## What It Produces

A single-page React app that renders ABC notation as a music staff. Features:
- ABC notation input textarea (paste or type a tune)
- Staff rendered with the `abcjs` library
- Instrument selector (Kora / Guitar / Piano — changes the instrument label in the staff header)
- Tempo slider (40–200 BPM) with a play/stop button
- Clean read-only display mode when given a `?tune=` URL parameter

---

## Paste This Prompt

```
Build a single-page React (Next.js app router) component called SheetMusicViewer.

Requirements:
- Import abcjs from "abcjs" (CDN OK, or npm install abcjs).
- Render an ABC notation staff from a textarea input. Default content:
  X:1\nT:Kelefaba\nM:4/4\nK:G\n|: G2AB c2BA | G4 D4 :|
- Add an instrument selector (Kora | Guitar | Piano) that prepends the
  chosen instrument name to the %%MIDI program line rendered by abcjs.
- Add a tempo slider (range 40–200, default 120 BPM) wired to abcjs's
  { defaultTempo: value } render option.
- Add a Play / Stop button that uses abcjs's TimingCallbacks to animate
  the current beat position as a highlight on the staff.
- Style with Tailwind CSS. Use a white card on a dark background (#0f172a).
  Staff background white, notation black. Controls below the staff in a
  row: instrument selector | tempo slider (with bpm readout) | play button.
- No authentication, no server calls, no external API. All state in React.
- Export default the component. Do not wrap in a page layout — just the card.
```

---

## Expected Output

A white music-notation card centered on a dark page. The staff shows the ABC tune. Clicking **Play** animates a moving highlight under the current beat. Changing the tempo slider updates the playback speed in real time. The instrument selector changes the `%%MIDI program` comment in the rendered header.

In v0.dev: deploy → share the `v0.dev/...` URL. The recipient can paste their own ABC tune and hit Play.

---

## Variations

1. **Read-only embed mode** — Add `if (typeof window !== 'undefined' && new URLSearchParams(window.location.search).get('tune'))` logic to pre-populate from a URL parameter. Useful for linking directly to a specific tune.
2. **Multi-part staff** — Change the default ABC to include two voices (V:1 and V:2) to show kora kumbengo + birimintingo staves side by side.
3. **Print layout** — Add a "Print / Save as PDF" button using `window.print()` with a `@media print` CSS rule that hides all controls and expands the staff to full width.
