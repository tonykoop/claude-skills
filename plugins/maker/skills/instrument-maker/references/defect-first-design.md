# Defect-First Instrument Design

**Origin capture:** tonykoop/claude-skills#382 (Move 37 provocation, 2026-06-19)

## Core inversion

Standard lutherie treats defects as degradation relative to a clean target: wolf-tones are suppressed, cracks are repaired, instabilities are damped. Defect-first design inverts this. The flaw — wolf-tone, crack, buckling collapse, rattle — is not noise to be filtered out; it is the seed the instrument is grown from.

The artifact IS the spec.

## Design procedure

1. **Name the defect** — describe it precisely: which frequency, which condition, which physical mechanism produces the anomaly. Wolf-tone at G3 on a cello body tuned to a given air-volume resonance. Crack-buzz from a bridging fracture under string tension. Rattle from a loose brace.

2. **Intentionally site it** — instead of suppressing, position the defect where it becomes a reliable, reproducible feature. Change the geometry, mass distribution, or joinery so the anomaly lands at a predictable pitch class or playing condition.

3. **Tune it** — treat the defect as a second instrument within the instrument. Use the same tuning logic you'd apply to a string or a bar: adjust mass/stiffness/damping until the defect lands at the intended pitch and has the intended sustain/decay profile.

4. **Engineer everything else to serve it** — the "correct" portions of the instrument (bore, belly, bridge, bracing) now exist to complement the designed defect rather than neutralize it. The wolf-tone stops being a failure mode and becomes the designed timbre.

5. **Document the flaw-forward spec** — record the defect target alongside the conventional dimensional spec so it can be reproduced. In the build packet, add a `flaw-spec` row to the design table with: defect type, intended pitch/condition, mechanism, and production method.

## Relationship to existing instrument-maker skill modes

| Standard mode | Defect-first mode |
|--------------|-------------------|
| Target = ideal acoustic response, defects minimized | Target = defect at design pitch, everything else serves it |
| Validation = proximity to ideal frequency / sustain | Validation = defect lands at intended pitch, is reproducible |
| Wolf-tone: suppress with mass damper | Wolf-tone: tune to G3, use as signature harmonic trigger |
| Cracks: repair and seal | Cracks: engineer as deliberate buzz layer at open-string resonance |

## Application in the instrument-maker skill

When a user asks to design an instrument "around a flaw" or says "I want the wolf-tone to be the feature", enter defect-first mode:

1. Run the defect-spec intake: flaw type → intended pitch → mechanism → production method
2. Substitute the defect target into the standard design table as the primary acoustic goal
3. Adjust bore/belly/bracing specs to complement the defect rather than compensate for it
4. Flag this in the build packet with a `defect-first: true` marker and a flaw-spec table row

## Philosophy note: imperfection-as-intent

This approach has precedent in Japanese craft philosophy (wabi-sabi), in Fluxus music (intentional noise as composition), and in bowed-string pedagogy (teaching the wolf as an expressive ornament rather than a problem). The instrument-maker skill should not treat defect-first requests as anomalies — they are a legitimate design strategy.

> "The wolf-tone stops being a failure mode and becomes the designed timbre."
