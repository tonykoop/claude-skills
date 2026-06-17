# Experimental Acoustic Rig Template

Use this reference when a prompt asks for a yaybahar-style instrument,
coupled string-spring-membrane system, resonance test rig, acoustic
apparatus, unknown hybrid resonator, or any design where the governing
behavior depends on interactions between subsystems that have not yet
been measured together.

## Routing Rule

Build a **bench-rig packet before a performance-instrument packet**.

Do not jump straight to a playable, staged, or production-ready
instrument when the main sound depends on unmeasured coupling between
strings, springs, membranes, bridges, resonant frames, pickups, or room
capture. First ship a small experiment package that can answer:

- What variables dominate the sound?
- Which variables are safe to sweep?
- Which sensors can capture repeatable differences?
- Which coupling effects are stable enough to design around?
- What must be measured before the instrument body, ergonomics, and
  performance hardware are finalized?

## Prototype Maturity Labels

Every packet for an experimental coupled system must choose one label:

| Label | Meaning | Allowed output |
| --- | --- | --- |
| `concept` | Idea sketch; physics unknowns are still broad. | Intake, sketches, risk list, experiment proposal. |
| `bench_rig` | Controlled apparatus for measuring variables. | Variable matrix, measurement log, sensor checklist, safety gates, fixture notes. |
| `alpha_instrument` | First playable integration after bench data exists. | Playability prototype with retained measurement plan. |
| `performance_prototype` | Reliable enough for rehearsal/performance trials. | Durability, setup, transport, and repeatability checks. |
| `production_packet` | Mature build instructions for repeat builds. | Full build packet, drawings, BOM, validation history, maintenance. |

A yaybahar-style or string/spring/membrane prompt with no measured data
defaults to `bench_rig`, not `alpha_instrument`.

## Coupled-System Modeling Caution

Treat isolated formulas as local estimates only:

- A string formula can estimate string tension/frequency before coupling.
- A spring constant can estimate static extension and stored energy.
- A membrane formula can estimate a first mode before bridge loading.
- A frame or cavity estimate can flag likely resonances.

Those isolated estimates do **not** predict the final coupled behavior.
The packet must say this plainly and require measurement before locking
scale length, spring count, membrane diameter, bridge material, pickup
placement, or performance ergonomics.

For coupled string-spring-membrane systems, validation is the design
method. The first deliverable is a repeatable experiment, not a finished
instrument claim.

## Required Bench-Rig Packet Outputs

A bench-rig packet includes these files at minimum:

- `README.md` — maturity label, experiment goal, setup overview.
- `variable-matrix.csv` — independent variables, levels, controls,
  response metrics, safety bounds.
- `measurement-log-template.csv` — one row per run or take.
- `sensor-capture-checklist.md` — audio/contact/environment capture
  setup and repeatability notes.
- `stored-energy-safety-checklist.md` — spring/string force, restraint,
  inspection, PPE, release path, and stop rules.
- `validation-plan.md` — staged expansion rule from coupon to subsystem
  to coupled rig to alpha instrument.
- `risks.md` — acoustic, structural, ergonomic, sensor, and safety risks
  with tests attached.

Optional files:

- `rig-layout.md` for fixture geometry and clamp positions.
- `excitation-protocol.md` for pluck, strike, bow, tap, scrape, or
  driven-shaker procedures.
- `data/` for recorded takes and processed measurements.
- `analysis-notebook.md` or `wolfram/` only after the capture protocol is
  stable enough to justify modeling.

## Standard `variable-matrix.csv`

Seed from `assets/templates/experimental-acoustic-rig/variable-matrix.csv`.

Required columns:

```csv
variable_id,subsystem,variable,baseline,levels,unit,control_or_independent,response_metrics,safety_bound,measurement_method,notes
```

Guidance:

- Use one variable per row.
- Mark fixed controls explicitly so future runs know what was held
  constant.
- Keep each sweep small. Do not change string tension, spring count,
  membrane tension, and bridge mass in the same first run.
- Put safety bounds in the matrix before the run, not after a near miss.

## Standard `measurement-log-template.csv`

Seed from
`assets/templates/experimental-acoustic-rig/measurement-log-template.csv`.

Required columns:

```csv
run_id,date_time,prototype_maturity,configuration_id,variable_changes,excitation_method,mic_distance_cm,mic_angle_deg,input_gain_db,contact_mic_mounting,environment,measured_frequency_hz,decay_time_s,peak_level_db,subjective_descriptors,raw_audio_path,photo_video_path,operator,notes
```

Each run should be repeatable by a different builder. If the log cannot
describe the setup, the result is not yet design evidence.

## Sensor And Capture Checklist

Seed from
`assets/templates/experimental-acoustic-rig/sensor-capture-checklist.md`.

Minimum capture fields:

- Microphone model and mic distance.
- Mic angle or orientation.
- Input gain and any limiter/compression state.
- Contact mic model and mounting location/material, if used.
- Environment: room, temperature, humidity, background noise, surface.
- Excitation method: pluck/strike/bow/tap/scrape/driver, tool, force
  proxy, repeat count.
- Subjective descriptors: attack, bloom, buzz, rattle, pitch stability,
  sustain, harshness, perceived coupling.

## Stored-Energy Safety Checklist

Seed from
`assets/templates/experimental-acoustic-rig/stored-energy-safety-checklist.md`.

Minimum safety gates:

- Estimate maximum string tension and spring extension before assembly.
- Use rated anchors, clamps, knots, crimps, and fasteners.
- Add a secondary restraint where a spring/string could release toward a
  person.
- Keep faces, hands, and cameras out of the release path.
- Inspect strings, springs, membranes, bridges, and anchors before every
  run.
- Define stop rules: visible cracking, slipping anchors, frayed string,
  spring deformation, uncontrolled oscillation, sharp fragments, or
  unexpected heating.

## Staged Expansion

Validation must expand in stages:

1. **Coupon:** measure one element by itself, such as a spring, membrane,
   bridge strip, or string under safe tension.
2. **Single subsystem:** combine two elements, such as string plus bridge
   or spring plus membrane.
3. **Coupled bench rig:** add the full string/spring/membrane path with
   adjustable fixtures.
4. **Alpha instrument:** add ergonomics and playable layout only after
   the coupled rig has repeatable measurements.
5. **Performance prototype:** add durable hardware, transport, tuning,
   and setup repeatability.
6. **Production packet:** only after multiple builds or repeat sessions
   confirm stable behavior.

If a stage produces unstable results, stay at that stage and revise the
variable matrix instead of advancing the maturity label.
