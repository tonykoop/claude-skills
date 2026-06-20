# Changelog — yoga-sequencer

## v1.9.0 — 2026-06-20

- Added `references/dji-mic-capture.md` defining the public DJI Mic capture manifest, Path A transcript/thematic split, Path B audio/playlist handoff, and capture-quality gate.
- Added `scripts/dji_mic_ingest.py` to validate capture manifests, extract thematic transcript spans, emit playlist-ready audio timelines, and block Rosetta readiness on loud music beds, high movement noise, dropouts, or clipping.
- Added pytest coverage for language/audio path splitting, music-bed blocking, movement/dropout findings, and empty transcript rejection.
- Source: Epic #368 story #375.

## v1.8.0 — 2026-06-20

- Added `references/reverse-sequence-engine.md` documenting the public Reverse Sequence Engine input, output, and human-review gate.
- Added `scripts/reverse_sequence_engine.py` to expand shorthand into a 60-minute class scaffold with phases, transition handoffs, script lines, playlist phase-map data, and review-gated trust status.
- Added pytest coverage for five-line shorthand expansion, macro expansion, transition handoffs, reviewer gating, and playlist phase metadata.
- Source: Epic #368 story #373.

## v1.7.0 — 2026-06-20

- Added `references/phase-gate-ingest.md` defining the captured-class JSON shape, four-array parse target, and anchor / triangulation / micro-batch / bulk go/no-go gates.
- Added `scripts/phase_gate_ingest.py` to parse class JSON into `metadata`, `audio_timeline`, `choreography_raw`, and `thematic_drops`, with fail-closed phase gates up through 35+ class bulk runs.
- Added pytest coverage for anchor parsing, micro-batch count gates, 35-class bulk acceptance, and malformed timing rejection.
- Source: Epic #368 story #372.

## v1.6.0 — 2026-06-20

- Added `references/rosetta-trainer.md` defining the shorthand-to-transcript parallel pair format, extracted labels, and explicit human-review quality bar.
- Added `scripts/rosetta_trainer.py` to parse shorthand/transcript pairs, extract somatic spacing, structural transitions, thematic-infusion terms, and return `trusted_for_training = false` until quality gates pass.
- Added pytest coverage for alignment labels, somatic spacing, thematic detection, and human-review blocking.
- Source: Epic #368 story #371.

## v1.5.0 — 2026-06-20

- Added `references/transition-matrix.json` with a public starter transition-vector model, multiple pathways into Crescent Lunge, transcript cue templates, and pacing-to-crossfade handoff settings.
- Added `scripts/transition_matrix.py` for deterministic target/pathway lookup and playlist/DJ crossfade handoff data.
- Added pytest coverage for Crescent Lunge multi-entry pathways, transcript cue mapping, and fast/medium/slow crossfade ordering.
- Source: Epic #368 story #370.

## v1.4.0 — 2026-06-20

- Added `references/shorthand-protocol.md` with the starter token table, side/orientation modifiers, breath operators, macro definition syntax, and a five-line sample class.
- Extended `scripts/engine_config.py` with full-coverage tokenization, inline macro definitions, and multiline shorthand program parsing so malformed shorthand fails loudly instead of dropping characters.
- Added pytest coverage for the documented five-line shorthand sample and unparsed-character rejection.
- Source: Epic #368 story #369.

## v1.3.0 — 2026-06-20

- Added `references/pose_thesaurus.json` with starter shorthand pose tokens, aliases, modifiers, operators, and the `Viny` macro expansion.
- Added `config.toml` as the public operator dashboard for `current_phase`, `syntax_strictness`, and `audio_sync.lufs_target`.
- Added `scripts/engine_config.py` so the engine can load the thesaurus and config at runtime, expand macros, and change behavior when strictness or LUFS settings change.
- Source: Epic #368 story #374.

## v1.2.2 — 2026-06-13

- `references/playlist-builder-handoff.md`: added worked 45-minute and 30-minute vinyasa phase-map YAML examples with contiguous timing, preserved warm-up/build/peak/cooldown/savasana phases, and required `energy` plus `cue_density` fields.
- SKILL.md: bumped version for the shorter-class playlist handoff examples.
- Source: Round 2 Henry implementation for issue #27.

## v1.2.1 — 2026-06-13

- `references/sequencing-principles.md`: mirrored the staple-pose safety boundary into mixed-level room defaults so reference-only loading still routes pigeon, lizard, deep twists, deep backbends, arm balances, inversions, and other constraint-sensitive shapes through `poses.yaml`.
- SKILL.md: bumped version and `last-updated` for the safety-boundary hardening.
- Source: Round 2 Henry implementation for issue #26.

## v1.2.0 — 2026-05-10

- Added `references/heated-room-safety.md` with a reusable teacher-facing hot-room checklist covering hydration, breath-quality gates, heat-distress signs, pregnancy / non-heated substitutions, and compression or inversion caution.
- SKILL.md now directs heated, hot power, sculpt, and C3-style requests to load the heated-room safety reference and include the checklist in full-class outputs.
- `references/sequencing-principles.md`: added heated-room cue-volume guidance so teacher voice gets quieter as repetition and heat rise.
- Source: Round 8 Bob hot-power vinyasa follow-on (issue #95).

## v1.1.0 — 2026-05-10

- Added cue-density arc as a required field on every phase of a full-class plan. Controlled vocabulary: `sparse`, `moderate`, `rhythmic`, `focused`, `minimal`.
- `references/sequencing-principles.md`: new "Cue density across the arc" section with default arcs for vinyasa (60/75/90), yin, restorative, and heated power vinyasa.
- `references/sequencing-principles.md`: new "Alternate-peak guidance" section with the regression-vs-alternate distinction, a constraint trigger list, and worked examples (Bound Side Angle, Bird of Paradise, Camel, Crow, Revolved Triangle).
- `references/playlist-builder-handoff.md`: formalized `cue_density` controlled vocabulary, clarified its independence from `energy`, and added a worked yin-class example so the schema is shown across non-vinyasa styles.
- SKILL.md: peak-pose-first mode now requires a teacher-discretion alternate peak when the default peak is constraint-heavy; sequencing rules and final check updated.
- Source: Round 7 TwinGrid Lane Dan blind run + Partner Peek (issue #69).

## v1.0.0 — 2026-05-09

- Initial skill: yoga session sequencing with pose safety boundaries.
- Lazy-load poses.yaml; inline playlist YAML for cross-platform portability.
- Staple-pose cheat-sheet safety boundaries tightened.
- Shorter-class playlist handoff worked examples added.
- Public-scrub pass: private names removed.
