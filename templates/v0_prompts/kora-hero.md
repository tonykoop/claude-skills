# Template: Kora-Hero Highway

**Target platform:** v0.dev (primary) · Replit Agent (also works)  
**Story:** #487  
**Date:** 2026-06-22

---

## What It Produces

A falling-note highway game in the style of Guitar Hero, tuned for kora:
- Two columns: **Left thumb** (blue) and **Right thumb** (orange)
- Notes fall from top; player presses `A` (left) or `L` (right) at the moment of contact
- Scoring HUD: combo multiplier, accuracy percentage, score
- BPM setting (default 90) — controls note-fall speed
- A preset pattern editor: choose from beginner patterns (Kelefaba) or intermediate (Jarabi)
- Game states: ready → playing → paused → game-over

This is a UI prototype. Keypress input simulates the real mic-tap detection that the full Expo Go version implements.

---

## Paste This Prompt

```
Build a React (Next.js app router) component called KoraHero — a
falling-note highway game for learning kora thumb patterns.

Layout:
- Full-screen dark background (#0a0a0f).
- Center a 400px-wide highway with two lanes: left (blue, key A) and
  right (orange, key L). Each lane is 180px wide with a 40px gap.
- At the bottom of each lane, render a "tap zone" circle (60px diameter).
  Highlight it white when the corresponding key is pressed.
- Notes are 60x20px rounded rectangles that fall from the top. Speed
  is proportional to BPM (at 90 BPM, a note takes 2 s to fall the full
  height; adjust linearly).

Game mechanics:
- Parse a note pattern array: { lane: 'L'|'R', beat: number }[].
  Beat 1 = first note. Notes are spaced by (60 / BPM) seconds each.
- When a note is within 30px of the tap zone and the player presses
  the correct key, score PERFECT (±15px) or GOOD (±30px).
  Miss = note exits bottom without a keypress.
- Scoring: PERFECT = 100 × combo, GOOD = 50 × combo, MISS resets combo to 1.
- Show a HUD in the top-right: Score | Combo ×N | Accuracy %.

Controls bar (below the highway):
- BPM slider (60–180, default 90) — updates fall speed in real time.
- Pattern selector: "Kelefaba (beginner)" | "Jarabi (intermediate)".
  Kelefaba pattern: alternating L R L R for 16 beats.
  Jarabi pattern: L L R L R R L R for 8 beats, repeat.
- Start / Pause / Restart buttons.

Style: Tailwind CSS. Neon glow on tap-zone hit (box-shadow: 0 0 12px).
No backend. All state in useState / useEffect. Requestanimationframe loop.
Export default the component.
```

---

## Expected Output

A dark full-screen game with two glowing columns. Notes fall at the set BPM tempo. Pressing `A` or `L` at the right moment lights up the tap zone and increments the score. The HUD shows live score, combo, and accuracy. Selecting "Jarabi" loads a syncopated pattern.

In v0.dev: deploy → share the `v0.dev/...` URL. Recipients need only a keyboard; no install, no mic.

For a version with real mic-tap detection (drum tap on the kora body), run the Expo Go recipe in [`../../docs/expo_preview.md`](../../docs/expo_preview.md) — mic input replaces the keyboard trigger.

---

## Variations

1. **MIDI input** — In Replit Agent, swap the keyboard listener for a Web MIDI API listener so a MIDI controller triggers each lane instead of keyboard keys.
2. **Note density ramp** — Add a "practice mode" where notes start sparse and gradually fill in over 4 repetitions of the pattern, building toward the full density.
3. **Custom pattern input** — Replace the selector with a text field accepting a shorthand like `L R L L R` so teachers can paste in any pattern from a lesson plan.
