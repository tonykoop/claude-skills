# Handoff prompt — Native American flute (NAF)

Paste the block below into a fresh Cowork or Claude Code chat.

---

You are Claude. Tony Koop just published a new skill called `sheet-music`
at https://github.com/tonykoop/sheet-music — it pairs with his
`instrument-maker-v4` skill to write playable music for the instruments
he builds. The repo is also at `C:\Users\Tony\Documents\GitHub\sheet-music\`
on this machine.

**Your task:** produce a complete starter songbook for an A-tuned
6-hole **Native American flute** (NAF), deposit it into the existing
`flutes` build repo, and write an honest evaluation of how well the
skill handled the v0.1 production-ready path.

The NAF (`naf-6hole` in the registry) is the v0.1 production-ready
instrument family. This should work *cleanly* end-to-end without you
having to invent things. If something feels rough or incomplete here,
that's a bug in the skill, not a v0.2 gap — and the evaluation should
say so.

**Steps:**

1. Read `SKILL.md`, then `references/flute-family.md` and
   `references/starter-songbook.md`. The NAF is `naf-6hole`: range
   A4–D6, A minor pentatonic, 6 holes, soundfont preset 76 (Pan
   Flute).

2. Pick **three public-domain tunes** that fit A minor pentatonic
   either natively or with minimal substitution:
   - Amazing Grace (already in `catalog/public-domain/hymn/` —
     pentatonic, transposes naturally)
   - Shenandoah (trad. American, mid-1800s — PD; lyrical, fits NAF
     range with one octave shift)
   - What Wondrous Love Is This (trad. Appalachian, 1811 — PD)

   The catalog already has Amazing Grace, Simple Gifts, and Twinkle
   Twinkle. Add any missing tunes to
   `catalog/public-domain/<tradition>/<slug>/` with `notes.md`
   documenting provenance. Pre-1929 US publication = PD; verify each
   before adding.

3. Compose **one Heifer Zephyr original** for the NAF. Use:
   ```
   python scripts/compose_original.py \
     --instrument naf-6hole \
     --slug <pick-a-name> \
     --mood "contemplative, slow, single-octave pentatonic" \
     --form AABA \
     --out catalog/original/<slug>/
   ```
   Then fill in the melody following `references/flute-family.md`'s
   NAF rules: pentatonic only, conjunct motion, sparse ornaments
   (zero or one per phrase), breath marks every 4–8 measures.

   Title: Heifer Zephyr brand voice — two or three words, evocative,
   no puns. "River Reed Waltz" is already used; pick something else.
   Strong directions: "Pre-Dawn Field," "Cottonwood Bend," "Dust
   Lullaby," "Slow River." Pick the best fit for the mood.

4. Run `scripts/deposit_songbook.py --instrument naf-6hole --target
   C:\Users\Tony\Documents\GitHub\flutes\` to deposit the songbook.
   The target build repo is `flutes` (Tony's NAFs ship from that
   generic flutes repo). The deposit lands at
   `flutes/learn-to-play/naf-6hole/` because multiple NAF variants
   share the `flutes` repo — that's by design, see `deposit_songbook.py`.

5. Verify post-deposit:
   - Each tune folder under `01-easy/` has `tune.abc`, `tune.mid`,
     `notes.md` minimum
   - `fingering-charts.svg` covers every distinct pitch in the songbook
   - `songsheet.pdf` rendered (ReportLab fallback is fine)
   - `flutes/README.md` got a "Learn to play" section appended
     pointing to the new folder

6. Run `scripts/validate_arrangement.py --target
   C:\Users\Tony\Documents\GitHub\flutes\learn-to-play\naf-6hole\
   --strict`. Fix anything it flags. Out-of-range pitches → transpose;
   missing files → regenerate.

**Deliverables (so the next person can evaluate cleanly):**

- `flutes/learn-to-play/naf-6hole/MANIFEST.md` — bullet list of every
  file you wrote, with a one-line purpose per file.
- `flutes/learn-to-play/naf-6hole/EVAL.md` — three sections:
  - **What worked** — production path is supposed to be clean here;
    confirm or refute.
  - **What felt rough** — anything that needed manual intervention,
    workaround, or extra context the skill didn't provide.
  - **v0.1 fixes** — bugs in the v0.1 skill that should be patched
    before v0.2 expands the family coverage.

Don't commit or push — Tony reviews changes via GitHub Desktop.
