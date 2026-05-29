# Yoga Sequencer Round 1 Eval

Date: 2026-05-08
Skill under test: `yoga-sequencer`
Runtime under test: shared portable skill contract
Evaluator: Codex

## Validation

- `python3 <skill-creator>/scripts/quick_validate.py skills/yoga-sequencer`
  Result: pass (`Skill is valid!`)
- YAML parse check:
  - `skills/yoga-sequencer/agents/openai.yaml`
  - `skills/yoga-sequencer/references/poses.yaml`
  - `manifest.yaml`
  Result: pass

## Benchmark 1

Prompt fixture:

> Use `$yoga-sequencer` to plan a 60-minute mixed-level vinyasa class around twisting and grounding. Keep both sides balanced and give me playlist-ready phase timing.

Expected mode or route:

- Theme-first sequencing

Expected artifacts:

- Class summary with length, level, theme, and energy
- Phase-by-phase sequence
- Warm-up, standing build, focal work, counterpose, cooldown, and savasana
- Playlist-builder handoff timing

Watch-points:

- Trigger accuracy
- Bilateral symmetry
- Coherent downshift
- Playlist handoff quality

Observed output summary:

- Produced a theme-led arc from seated breath to spinal warm-up, lunge and warrior twist work, a revolved standing focal section, seated and supine unwinding, then savasana.
- Included mirrored work on both sides and left enough room for cooldown instead of spending the full class in standing flow.
- Emitted a six-phase handoff block with contiguous timings suitable for `yoga-playlist-builder`.

Result:

- Pass

Notes:

- Strong fit for the core acceptance case. The skill's reference structure made it easy to keep the output balanced and phase-aware without bloating the main skill body.

## Benchmark 2

Prompt fixture:

> Use `$yoga-sequencer` to build a 45-minute vinyasa class that peaks in crow. The room is mixed-level and a few students are wrist-sensitive. Include modifications and a playlist-builder handoff.

Expected mode or route:

- Peak-pose-first sequencing

Expected artifacts:

- Preparation ladder for crow
- Wrist-aware regressions
- Peak section with exit ramp
- Playlist-builder handoff timing

Watch-points:

- Safe progression into an advanced pose
- Constraint handling
- Counterpose quality after wrist loading
- Context discipline

Observed output summary:

- Built from wrist prep, core activation, malasana compression work, plank-based heat, and crow attempts into hand relief, child's pose, supine release, and savasana.
- Offered simpler options such as squat hold, toes-on-block, and plank instead of forcing crow attempts.
- Treated wrist sensitivity as a planning constraint rather than a medical claim and reserved only a short window for peak attempts.

Result:

- Pass

Notes:

- This benchmark confirms the skill handles advanced-pose ambition without skipping prep or cooldown. The `poses.yaml` starter library gave enough support for practical modifications.

## Benchmark 3

Prompt fixture:

> Use `$yoga-sequencer` to give me counter-poses after camel in a mixed-level vinyasa class, and tell me whether I want a full opposite shape or a neutral reset first.

Expected mode or route:

- Counter-pose lookup

Expected artifacts:

- What camel loads most heavily
- Two to five counter-shapes
- Guidance on neutral reset versus strong reversal

Watch-points:

- Lookup-mode brevity
- Correct counter-pose reasoning
- No unnecessary full-class output

Observed output summary:

- Identified camel as a strong backbend with quad, hip-flexor, chest, and neck load.
- Recommended a neutralizing transition first, then options like child's pose, a neutral seat, supine twist, or a soft fold rather than an aggressive opposite shape.
- Kept the answer compact and avoided expanding into a full class plan.

Result:

- Pass

Notes:

- This shows the skill can stay small when the request is a lookup instead of a complete sequence.

## Deviations Fixed During Quality Gate

- Removed unsupported `version` and `last-updated` keys from `SKILL.md` frontmatter so the bundled `quick_validate.py` passes.
- Removed the per-skill `CHANGELOG.md`, which `skill-creator` treats as extraneous documentation.
- Added `agents/openai.yaml` using the bundled generator.
- Added a table of contents to `references/sequencing-principles.md` because it exceeds 100 lines.

## Residual Risks

- `poses.yaml` is intentionally a starter library, so unusual peak poses will still require judgment rather than exhaustive catalog lookup.
- The benchmark runs in this round are manual contract evaluations, not an automated harness with independent model execution.

## Round 2: Cross-Platform Smoke Eval (2026-05-08)

Re-ran the same three prompt fixtures against the updated skill to validate lazy-loading and inline-YAML-handoff changes.

- Validation: `quick_validate.py` pass; YAML parse pass for `poses.yaml`, `agents/openai.yaml`, `manifest.yaml`.
- Benchmark 1 (twists + grounding, 60 min): pass. Skipped `poses.yaml`; staple cheat-sheet sufficient. Inline phase-map YAML emitted. Bilateral symmetry intact.
- Benchmark 2 (crow peak, 45 min, wrist-sensitive room): pass. Opened `poses.yaml` because of the constraint, exactly as the lazy-load rule prescribes. Wrist-aware parallel track from arrival through cooldown, published exit ramp from crow. Inline phase-map YAML emitted, compressed proportionally for 45 min.
- Benchmark 3 (camel counter-pose lookup): the agent skipped `poses.yaml` and produced a reasonable answer from general teaching knowledge. Treat this as a soft pass on output quality but a contract regression — see Round 3 below.

### Cross-platform notes from this round

- The "load references on demand" framing is doing real work — agents skip `poses.yaml` for routine class plans and open it for explicit constraints, which is the correct pattern for mobile and zip-uploaded installs.
- Reframing playlist handoff as "always emit YAML inline" removes a hidden dependency on `yoga-playlist-builder` being installed. The block now stands on its own across Claude Desktop, Claude mobile zip uploads, Codex, and Gemini.

## Round 3: Owner Review Fixes (2026-05-08)

Owner of the original yoga-sequencer requested three contract corrections after Round 2. All three are now applied.

### Issue 1: cheat-sheet was too permissive about constraint-sensitive poses

The Round 2 staple cheat-sheet lumped lizard, pigeon, malasana, bridge, etc. into the "no `poses.yaml` lookup required" group. Those shapes have real, frequent failure modes (knees, SI joint, neck) that the bundled library tracks explicitly, so encouraging Claude to skip the file for them is unsafe.

**Fix:** Split the cheat-sheet into two tiers in `SKILL.md` — Tier 1 (safe defaults, no lookup) and Tier 2 (constraint-sensitive staples, always cross-reference `poses.yaml`). Tier 2 explicitly lists hip openers (malasana, lizard, pigeon, reclined figure four), backbends (bridge, locust, camel), arm balances and inversions (crow), and deep twists (revolved triangle, revolved crescent).

### Issue 2: Round 2 Benchmark 3 was a contract miss

Counter-pose lookups should always open `poses.yaml` because the `counterposes_for` and `contraindications` fields are how the library encodes the right neutralizers. The Round 2 camel test reported "skipped `poses.yaml`" as a pass, but that's exactly the failure mode the bundled library exists to prevent (e.g., recommending a deep forward fold straight after camel).

**Fix:** Tightened the Counter-pose lookup mode in `SKILL.md` to mandate opening `poses.yaml` and to list the specific fields (`counterposes_for`, `contraindications`, `focus`, `intensity`, `family`) that drive the answer. Added the same rule to the "Always open `poses.yaml`" list under the cheat-sheet.

**Re-test (Round 3 Benchmark 3, camel counter-pose):** pass. The agent opened `poses.yaml`, found camel's contraindications (`neck_sensitivity, low_back_compression, knee_sensitivity`), and located the `counterposes_for: [camel]` relationships on `downward_dog`, `seated_twist`, and `supine_twist`. Output started with a neutral reset (child's pose, down dog) before the gentle counter-shapes, which is the correct mixed-level recommendation. Stayed in lookup brevity, correctly skipped the playlist phase-map YAML.

### Issue 3: playlist handoff contract was ambiguous

Round 2 phrasing ("always emit when the user wants music or playlist-ready timing") left it unclear whether full class plans without the word "music" should still get the YAML.

**Fix:** Added an unambiguous rule block under Output shape in `SKILL.md` — "When to include the playlist phase-map YAML" — with explicit always/skip lists. The phase-map block is now declared part of the contract for any full class plan, with lookup-only requests as the explicit exception. `references/playlist-builder-handoff.md` updated to reference the SKILL.md rule as authoritative and reinforce the same contract.

### Validation (Round 3)

- `python3 .../skill-creator/scripts/quick_validate.py skills/yoga-sequencer`: pass
- YAML parse for `poses.yaml`, `agents/openai.yaml`, `manifest.yaml`: pass
- Re-test of Benchmark 3 against the corrected skill: pass — see Issue 2 above.

### Residual minor follow-ups (not blocking)

- 45-minute worked example for the playlist handoff schema (proportional-compression rule works, but a worked example would save a step).
- Slight redundancy between the Tier 2 cheat-sheet and the "Always open `poses.yaml`" bullet list. Reinforcing rather than contradictory; left as-is for now.
