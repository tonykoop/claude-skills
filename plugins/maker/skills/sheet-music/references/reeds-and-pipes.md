# Reeds & pipes — notation and arrangement rules

**v0.1 status: skeleton.** The conventions below are documented for the
skill to reference, but the rendering scripts handle this family more
loosely until v0.2. Bagpipes are explicitly on the v0.2 roadmap (Tony
called out bagpipe ornament rules as a key motivator for this skill).

## Subfamily map

| Subfamily | Examples | Sound source | Defining feature |
|---|---|---|---|
| single-reed | chalumeau, clarinet | beating reed against mouthpiece | register-key leap, tongued articulation |
| double-reed | duduk | two reeds vibrating together | warm low end, glides between most notes |
| bagpipe (future) | Great Highland chanter | enclosed reed driven by bag | continuous-air, no rests, mandatory grace clusters |

## Notation conventions (single reeds)

Treble staff. Clarinet transposes (B-flat clarinet sounds a major 2nd
lower than written), so the ABC for clarinet is at *written* pitch
with a header note explaining the transposition. Chalumeau is concert.

- Slurs are heavily used — single-reeds breathe-articulate phrases
  rather than tonguing every note.
- Register-key leap (clarinet only): mark with a small bracket above
  the leap point.
- Dynamic shaping (`p`, `mp`, `mf`, `f`) is more meaningful than for
  flutes; include it in clarinet songsheets.

## Notation conventions (double reeds — duduk)

Treble staff in concert pitch. The duduk's hallmark is the *dam* drone
(a second player holds a sustained tone) and microtonal glides between
adjacent scale degrees.

- Duduk-glide: notate as a slur with a wavy line above (or `(de)` plus
  a margin "glide" note in ABC).
- Microtonal bend: notate as the principal pitch with a curved arrow
  showing the bend direction; explain in `notes.md`. Don't use
  quarter-tone accidentals — the skill's MIDI/notation pipeline doesn't
  reliably round-trip them.
- Dam drone: in ensemble arrangements, write it on a second staff. In
  solo arrangements, treat it as implicit and note in `notes.md`.

Range: `range_low` to `range_high` from the duduk registry row. Most
trad duduk repertoire stays in the lower octave for warmth; the upper
octave is for emphasis.

## Notation conventions (bagpipes — v0.2)

Reserved. Documenting here so future-me has the roadmap.

The Great Highland chanter has a 9-note A-mixolydian scale (low G, low
A, B, C#, D, E, F#, high G, high A). All ornaments are explicit
*grace-note clusters* notated with small notes between the principal
notes. The big ones:

- **Doubling** — three grace notes (G-D-G or similar) before the
  principal. Almost every long note in pipe-band repertoire has one.
- **Throw on D** — F-A-G-D cluster.
- **Grip** — G-D-G cluster between two principals.
- **Birl** — repeated low-A notes with a low-G grace between.
- **Taorluath, crunluath** — complex compound ornaments for piobaireachd
  (advanced; not for beginner songbooks).

Bagpipe music has *no rests* — the bag stores air, so the chanter never
stops sounding. Phrasing is articulated entirely through grace-note
clusters, not silences. Beginner pipe-band arrangements still require
correct embellishment; the embellishments *are* the rhythm.

Tony's chalumeau-as-chanter experiments may give us a way to bring some
of this notation to a single-reed instrument that can actually take
rests. v0.2 will add a "chanter-style ornamented" mode that uses the
embellishment vocabulary even when the underlying instrument doesn't
require continuous air.

## Arrangement workflow (skeleton)

1. Read the registry row. Note the transposition.
2. Pick a tune in a key the instrument plays cleanly.
3. Transpose if needed (write at written pitch for transposing
   instruments; sounding pitch for non-transposing).
4. Add idiom-specific markings (slurs for single-reeds, glides for
   duduk, embellishments for bagpipes once v0.2 lands).
5. Generate fingering chart from the registry's fingering scheme.
6. Run the standard render pipeline.
7. Write `notes.md` explaining transposition, glides, and any
   tradition-specific notation the player may not recognize.

## Quality gates specific to this family

- Clarinet ABC sources are at *written* pitch; flag if the `K:` line
  doesn't match the transposition expected for B-flat.
- Duduk arrangements that lack `notes.md` glide guidance are flagged
  by `validate_arrangement.py`.
- Bagpipe arrangements without doublings on long notes are flagged
  (v0.2 only — bagpipes are skeleton in v0.1).
