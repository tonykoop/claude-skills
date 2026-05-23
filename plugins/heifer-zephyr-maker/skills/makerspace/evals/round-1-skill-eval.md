# Makerspace Round 1 Skill Eval

Date: 2026-05-08
Skill path: `<your-workspace>/makerspace`
Issue context: `<your-repo>#15`

## Scope

This pass re-checked the revised `makerspace` skill against
`skill-creator/SKILL.md`, ran structural
validation, and attempted a CLI forward-test before falling back to an
in-process manual behavioral pass.

## Conformance check against `skill-creator`

### Fixes made

- Removed root `CHANGELOG.md`.
- Removed `evals/workspace/README.md`.
- Removed the `CHANGELOG.md` artifact entry from `manifest.yaml`.
- Rewrote `SKILL.md` in a more imperative, resource-driven style.
- Added top-level tables of contents to long references that this revised
  skill explicitly points at:
  - `references/manufacturing-and-tools.md`
  - `references/sourcing-and-production.md`
  - `references/space-profile-schema.md`
  - `references/doe-integration.md`
- Restored the pre-existing root `README.md` and `getting-started.md` after
  confirming they are repo-level documentation, not newly-added runtime skill
  clutter.

### Correction

`skill-creator` is a good rule for avoiding new low-signal docs inside a
skill package, but it should not be applied by deleting pre-existing repo
documentation blindly. The corrected interpretation for this repo is:

- keep `SKILL.md` and the runtime resources lean
- avoid adding new auxiliary docs just for the skill workflow
- preserve existing repo-level docs unless the user asks for a broader repo
  cleanup

### Remaining conformance notes

- Existing repo docs such as `README.md`, `getting-started.md`, and
  `spaces/README.md` remain in place. They are outside the trigger path for
  the runtime skill and are being treated as repository documentation rather
  than new skill clutter.
- Some example packet folders still contain user-facing docs. They are outside
  the core trigger path, but they are still less minimal than the
  `skill-creator` guidance prefers.
- Legacy v0.2 packet machinery remains in the repo for compatibility and
  benchmarking. The revised `SKILL.md` explicitly treats it as optional
  historical context rather than the default runtime contract.

## Structural validation

### `quick_validate.py`

Command:

```bash
python3 <skill-creator>/scripts/quick_validate.py <your-workspace>/makerspace
```

Result:

```text
Skill is valid!
```

### YAML / frontmatter / JSON checks

Checks run:

- `SKILL.md` frontmatter exists.
- `SKILL.md` frontmatter parses as YAML.
- `SKILL.md` frontmatter contains only `name` and `description`.
- `agents/openai.yaml` parses as YAML.
- `assets/templates/shop-equipment-profile.yaml` parses as YAML.
- `manifest.yaml` parses as YAML.
- `evals/evals.json` parses as JSON.

Result: pass.

## Behavioral benchmark

### Method

Attempted first:

```bash
codex exec --ephemeral -s read-only -C <your-workspace>/makerspace ...
```

Observed failure:

```text
failed to connect to websocket: Operation not permitted (os error 1)
```

Because this sandbox blocks outbound network access, a true external CLI
forward-test was not available. The benchmark below is therefore an
in-process manual forward-test against the revised skill contract. Timing is
not available for the successful behavioral pass. The only CLI timing data is
for the blocked run, which failed before inference.

### Prompt 1

Type: CNC jig decision

Prompt:

```text
I'm at Maker Nexus and need a jig decision for drilling repeatable 6 mm dowel
holes in twelve maple cabinet side panels. Hole location needs to stay within
plus or minus 0.005 inch from the front edge, and I want setup time to drop
after the first part. I have CNC-router and woodshop access. Should I make a
dedicated drill jig, adapt a fence-and-stop setup, or use the CNC as the
locating fixture? Give me the decision, the workholding logic, the fallback
route, and the safety checks.
```

Expected behavior:

- Separate design intent from machine operations.
- Compare at least the three candidate approaches.
- Name datums, restraint, first-article checks, and a fallback route.
- Include machine-aware safety checks.

Observed behavior:

- Recommended using the CNC as the locating fixture for the primary route,
  with a spoilboard-backed fence-and-hard-stop registration setup rather than
  a fully separate dedicated drill jig.
- Rejected a dedicated drill jig as overbuilt for quantity 12 and the stated
  machine access.
- Kept a fence-and-stop drill-press route as fallback if CNC availability or
  probing/setup confidence becomes the blocker.
- Identified the critical datum from the panel front edge and called for a
  first-article location check before running the batch.
- Included clamp-clearance, safe-Z, spoilboard flatness, and tool stick-out
  concerns in the safety/workholding logic.

Pass/fail: pass
Timing: not available; external runner blocked

### Prompt 2

Type: make / order / buy / borrow fixture choice

Prompt:

```text
I have a home shop with a handheld router, drill press, jigsaw, flush-trim
bits, and clamps. I need to make eight matching ash chair arms with a sweeping
outside curve. Help me decide whether I should make a router template, order
one, buy a commercial template, or borrow shop tooling. I care more about
repeatability than speed.
```

Expected behavior:

- Produce an explicit make/order/buy/borrow recommendation.
- Weigh reuse, lead time, accuracy, and shop capability.
- Provide a repeatable fabrication route rather than a generic opinion.

Observed behavior:

- Recommended making a dedicated MDF or plywood router template in the home
  shop because the geometry is custom, the batch is meaningful, and the tool
  access already supports rough-cut plus flush-trim production.
- Rejected commercial purchase and ordering because the geometry is unlikely
  to match and lead time does not beat a same-day template build.
- Treated borrowing as low-confidence because the prompt gives no known access
  to a compatible shared jig.
- Preserved repeatability by leaning on a first-article template check,
  reference edge registration, and a trace/rough-cut/flush-trim sequence.

Pass/fail: pass
Timing: not available; external runner blocked

### Prompt 3

Type: machine-aware shop packet

Prompt:

```text
I'm laser-cutting a batch of acrylic spacers at Maker Nexus and need a carrier
fixture so small parts don't shift after the final contour cut. I also need a
quick safety review because the stock comes with protective film and I want to
avoid flare-ups. Give me the repeatable shop packet.
```

Expected behavior:

- Produce the compact packet shape instead of drifting back to the old broad
  build-packet contract.
- Include fixture concept, workholding logic, safety checks, and a sourcing
  decision.
- Stay machine-aware for laser behavior and small-part retention.

Observed behavior:

- Stayed inside the compact fabrication-packet shape rather than expanding
  into portfolio artifacts.
- Chose a carrier or window-frame retention strategy for small-part control,
  with workholding logic focused on part retention after contour completion.
- Surfaced laser-specific safety concerns: flare risk from film, air-assist
  dependence, stop-work conditions for flame or residue buildup, and material
  checks before cutting.
- Implied that the fixture should be made or adapted locally rather than
  special-ordered, because speed-to-use and machine fit dominate the choice.

Pass/fail: pass
Timing: not available; external runner blocked

## Workspace recommendation

Keep `evals/workspace/` in the repo as preserved historical benchmark
artifacts. That location is sensible for this repo because it keeps the old
workspace data versioned with the skill while avoiding runtime coupling.

Keep the original external `makerspace-workspace` folder untouched for now.
Do not delete or move the original until the repo owner explicitly asks, since it may
still be a useful provenance anchor or comparison point.

If the repo gets another cleanup pass later, consider renaming the in-repo
copy to `evals/workspace-legacy-v0.2/` to make its status even clearer.

## Remaining risks

- True CLI forward-testing is still blocked by the no-network sandbox, so the
  behavioral pass here is honest but not independent.
- Legacy helper docs remain in some subfolders outside the main trigger path.
- Legacy specialists and references for the older broad build-packet model are
  still present; the new `SKILL.md` de-emphasizes them, but a future pruning
  pass would reduce ambiguity further.
- `references/empirical-learning-loop.md` had pre-existing local changes that
  were intentionally left alone during this pass.
