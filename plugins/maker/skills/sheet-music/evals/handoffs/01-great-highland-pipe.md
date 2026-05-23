# Handoff prompt — Great Highland Pipe

Paste the block below into a fresh Cowork or Claude Code chat.

---

You are Claude. Tony Koop just published a new skill called `sheet-music`
at https://github.com/tonykoop/sheet-music — it pairs with his
`instrument-maker-v4` skill to write playable music for the instruments
he builds. The repo is also at `C:\Users\Tony\Documents\GitHub\sheet-music\`
on this machine.

**Your task:** use the skill to produce a complete starter songbook for
the **Great Highland Pipe** (Scottish bagpipe) and write an honest
evaluation of how well the skill handled it.

This is a stress test. Bagpipes are the case Tony specifically called
out as having unique notation requirements (no rests, mandatory grace
clusters, 9-note A-mixolydian chanter). The skill's v0.1 release marks
the bagpipe family as **skeleton-only** with full support deferred to
v0.2 — so expect to do work the skill doesn't fully automate yet, and
report what you had to invent.

**Steps:**

1. Read `SKILL.md`, then `references/reeds-and-pipes.md`. Internalize
   the bagpipe-specific rules — especially that the chanter never
   stops sounding (no rests, ever) and that phrasing is articulated
   entirely through grace-note clusters.

2. Add a row to `instruments/registry.yaml` under the
   `reeds-and-pipes:` family:
   - id: `great-highland-pipe`
   - display_name: `Great Highland Pipe (chanter)`
   - subfamily: `bagpipe`
   - build_repo: `tonykoop/great-highland-pipe` (placeholder; no build
     repo exists yet)
   - range_low: G4, range_high: A5
   - transposition: concert (technically GHP "low A" sounds closer to
     B♭4, but standard pipe notation writes it as A — note this in the
     row's `notes:` field)
   - key_default: A
   - scale: `mixolydian-A`
   - fingering: `ghp-chanter-9note`
   - ornaments: `doubling`, `throw-on-d`, `grip`, `birl`, `taorluath`
   - soundfont_preset: 110 (GM Bagpipe)
   - notes: capture the air-driven-no-rest constraint

3. Add a placeholder fingering JSON at
   `assets/fingering-icons/ghp-chanter-9note.json` with the 9 standard
   chanter notes (low G, low A, B, C-sharp, D, E, F-sharp, high G,
   high A) and 8 holes (7 finger holes + 1 thumb hole). Mark
   `placeholder: true` since you don't have authoritative measurements.

4. Pick **three public-domain pipe tunes**. Suggested:
   - Scotland the Brave (lyrics 1820s, melody older — verify PD in US)
   - Loch Lomond (~1841 lyrics, melody older — PD)
   - Auld Lang Syne (Burns 1788, melody trad. — PD)

   Verify each is PD before transcribing. Write the canonical ABC
   under `catalog/public-domain/celtic/<slug>/tune.abc`. Apply pipe-
   band conventions: doublings on long notes, throws on D, grace
   clusters between repeated pitches. **No rests anywhere.**

5. Compose **one Heifer Zephyr original** for the GHP. Use
   `scripts/compose_original.py --instrument great-highland-pipe`.
   Slow march tempo (70-80 bpm), AABA, 9-note scale only,
   ornament-rich. Title in Heifer Zephyr brand voice — two or three
   words, evocative, no puns ("Stone Cairn," "Drone Path," etc.).

6. Deposit the songbook into
   `C:\Users\Tony\Documents\GitHub\sheet-music\examples\great-highland-pipe-songbook\`
   (since there is no GHP build repo yet). Use the standard
   `learn-to-play/` shape from `references/starter-songbook.md`:
   00-warmup-scales, 01-easy (3 PD tunes), 02-intermediate (2 of those
   tunes re-arranged with denser ornamentation), 03-original (the
   Heifer Zephyr piece), `fingering-charts.svg`, `songsheet.pdf`,
   `README.md`.

7. Run `scripts/render_pipeline.py` on each tune. Audio rendering will
   probably skip (no soundfont expected); fingering and MIDI must
   succeed. Run `scripts/validate_arrangement.py` on each tune in
   strict mode and fix what it flags.

**Deliverables (so the next person can evaluate cleanly):**

- `examples/great-highland-pipe-songbook/MANIFEST.md` — bullet list of
  every file you wrote, with a one-line purpose per file.
- `examples/great-highland-pipe-songbook/EVAL.md` — three sections:
  - **What worked** — parts of the skill that handled GHP cleanly.
  - **What didn't** — where you had to invent rules or work around
    skeleton coverage. Be specific (file path + what was missing).
  - **v0.2 recommendations** — concrete diffs to
    `references/reeds-and-pipes.md`, `instruments/registry.yaml`, or
    scripts that would make GHP production-ready.

Don't commit or push — Tony reviews changes via GitHub Desktop.
