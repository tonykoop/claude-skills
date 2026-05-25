# Handoff prompt — Marimba

Paste the block below into a fresh Cowork or Claude Code chat.

---

You are Claude. Tony Koop just published a new skill called `sheet-music`
at https://github.com/tonykoop/sheet-music — it pairs with his
`instrument-maker-v4` skill to write playable music for the instruments
he builds. The repo is also at `C:\Users\Tony\Documents\GitHub\sheet-music\`
on this machine.

**Your task:** produce a starter songbook for a **4.3-octave concert
marimba** (range C3–F7, fully chromatic, 2-mallet beginner technique)
and write an honest evaluation of how well the skill handled it.

This is the "**add a new instrument**" path. Marimba is **not** in the
registry yet, and pitched percussion is skeleton-only in v0.1. You'll
exercise the parts of the skill that handle:

- adding a new instrument cleanly
- pitched percussion that needs a different "fingering" abstraction
  (bar layout, not finger holes)
- chromatic scale (not pentatonic) — different from tongue drum

**Steps:**

1. Read `SKILL.md`, then `references/percussion.md` (especially the
   "pitched percussion: tongue drum, hang" section, which sets the
   precedent for marimba), and the "Adding a new instrument" recipe
   in `SKILL.md`.

2. Add a row to `instruments/registry.yaml` under the `percussion:`
   family:
   - id: `marimba`
   - display_name: `Marimba (4.3-octave concert)`
   - subfamily: `idiophone-pitched`
   - build_repo: `tonykoop/marimba` (placeholder; no build repo yet)
   - range_low: C3, range_high: F7
   - transposition: concert
   - key_default: C
   - scale: chromatic (this is the differentiator from tongue drum,
     which is pentatonic)
   - fingering: `marimba-bar-layout`
   - ornaments: `mallet-roll`, `dead-stroke`, `tremolo`
   - soundfont_preset: 13 (GM Marimba)
   - notes: 4-mallet technique is advanced; v0.1 arrangements stay
     2-mallet (single melodic line + occasional simple harmony bar)

3. Decide how the marimba's "fingering chart" should work. Marimba
   players read standard staff, not finger diagrams. Two reasonable
   options:
   (a) Skip the per-pitch fingering renderer entirely; produce a
       single "**bar layout diagram**" showing the marimba keyboard
       with the songbook's pitch range highlighted.
   (b) Adapt the fingering renderer to emit bar-position diagrams
       (one per pitch).

   Pick **(a)** for v0.1. Add a placeholder JSON at
   `assets/fingering-icons/marimba-bar-layout.json` with
   `placeholder: true` and a note explaining the bar-layout design
   intent. The songbook will substitute `bar-layout.svg` for
   `fingering-charts.svg`.

4. Pick **three public-domain tunes** appropriate for a beginner
   marimba player (single-line melody, no harmony):
   - Twinkle Twinkle Little Star (already in catalog; classic
     beginner mallet piece)
   - Ode to Joy (Beethoven, 1824 — PD in US)
   - Greensleeves (trad. English, 1580 — PD)

   Verify PD status; add any missing tunes to
   `catalog/public-domain/<tradition>/<slug>/`.

5. Compose **one Heifer Zephyr original** for the marimba. Use:
   ```
   python scripts/compose_original.py \
     --instrument marimba \
     --slug <pick-a-name> \
     --mood "bright, conjunct, idiomatic marimba" \
     --form AABA
   ```
   Marimba originals can use chromatic motion (unlike pentatonic
   flute originals). Title: Heifer Zephyr brand voice — two or three
   words. "Sunrise Bell," "Wood Glow," "Morning Bars" are starters;
   pick the best.

6. Write the deposit into
   `C:\Users\Tony\Documents\GitHub\sheet-music\examples\marimba-songbook\`
   (since there's no marimba build repo). Use the standard
   `learn-to-play/` shape but replace `fingering-charts.svg` with
   `bar-layout.svg` (a single image of the marimba keyboard with the
   songbook's pitch range marked).

7. Run `scripts/render_pipeline.py` on each tune. The fingering
   renderer will produce SVGs marked as "placeholder" — that's
   expected per the choice in step 3. Manually generate the
   `bar-layout.svg` with the keyboard visualization.

**Deliverables (so the next person can evaluate cleanly):**

- `examples/marimba-songbook/MANIFEST.md` — bullet list of every file
  you wrote, with a one-line purpose per file.
- `examples/marimba-songbook/EVAL.md` — three sections:
  - **What worked** — parts of the new-instrument path that handled
    marimba cleanly.
  - **What didn't** — where pitched-percussion-with-chromatic-scale
    felt incomplete relative to the flute path.
  - **v0.2 recommendations** — concrete proposals:
    - Should the "fingering" abstraction be replaced with "layout
      diagram" for pitched-idiophone instruments?
    - How should the songbook indicate mallet choice (hard / medium
      / soft) per tune?
    - Does `references/percussion.md` need a separate "pitched-
      keyboard percussion" section distinct from "tongue drum / hang"?

Don't commit or push — Tony reviews changes via GitHub Desktop.
