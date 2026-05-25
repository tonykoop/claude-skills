# Makerspace Round 2 Cross-Platform Smoke Eval

Date: 2026-05-08
Skill path: `skills/makerspace` (portable snapshot in `tonykoop/claude-skills`)
Handoff: `docs/handoffs/2026-05-08-claude-cross-platform-review/05-makerspace.md`

## Scope

Re-validate the portable snapshot after the cross-platform-review fixes:

- Legacy `evals/workspace/` moved out of the package to
  `docs/benchmarks/makerspace/`.
- `spaces/`, `scripts/`, `examples/` brought in from the standalone
  `tonykoop/makerspace` repo for parity with what `SKILL.md` and the
  reference docs assume.
- `SOURCE_COMMIT.md` and `scripts/sync_makerspace_snapshot.sh` added so
  the snapshot can be re-synced on release without drift.

## Structural validation

- `quick_validate.py`:
  `python3 /home/tony/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/makerspace`
  → `Skill is valid!`
- `scripts/validate_packaged_paths.py skills/makerspace` → ok. This new
  validator walks every YAML/JSON value inside the package and fails if
  any value resolves to a path outside the skill (e.g.
  `../../../docs/...` or absolute paths leaving the skill root). It is
  also called automatically at the end of `sync_makerspace_snapshot.sh`
  so a future sync that re-introduces an out-of-package pointer fails
  loud rather than silently shipping a broken zip.
- YAML/JSON parse: 7 YAML files + 1 JSON file all parse; SKILL.md
  frontmatter has only `name` and `description`. Files checked:
  - `agents/openai.yaml`
  - `assets/templates/doe-study-template.yaml`
  - `assets/templates/shop-equipment-profile.yaml`
  - `manifest.yaml`
  - `spaces/_template/profile.yaml`
  - `spaces/home-shop-default/profile.yaml`
  - `spaces/maker-nexus/profile.yaml`
  - `evals/evals.json`
- Cross-reference check: every reference, specialist, and shop profile
  named in `SKILL.md` resolves to a real file inside the package.

## Package size

- Before: 1.5 MB (1.3 MB of which was the legacy v0.2 benchmark
  workspace)
- After: ~210 KB (skill body + spaces + scripts + examples)

This puts the skill comfortably inside mobile zip-upload limits.

## Behavioral pass (in-process)

True external CLI forward-test is still blocked in this sandbox
(`failed to connect to websocket: Operation not permitted` per the
round-1 doc). The pass below is an in-process forward-test against the
revised `SKILL.md` contract.

### Prompt 1 — drill-jig decision

> I'm at Maker Nexus and need a jig decision for drilling repeatable
> 6 mm dowel holes in twelve maple cabinet side panels. Hole location
> needs to stay within plus or minus 0.005 inch from the front edge,
> and I want setup time to drop after the first part. I have CNC-router
> and woodshop access. Should I make a dedicated drill jig, adapt a
> fence-and-stop setup, or use the CNC as the locating fixture? Give me
> the decision, the workholding logic, the fallback route, and the
> safety checks.

Expected: separate design intent from machine ops; compare three
candidate approaches; name datums, restraint, first-article check, and
fallback; include machine-aware safety checks.

Observed: the SKILL.md workflow walks straight from the Maker Nexus
shop profile (`spaces/maker-nexus/profile.yaml` now resolves inside the
package) into design intent (panel front-edge datum, ±0.005 in
tolerance), then a three-way comparison
(`references/jig-decision-matrix.md`) with the CNC-as-fixture route
chosen, a fence-and-stop drill-press fallback, and a safety pass via
`references/safety-checklist.md`. Pass.

### Prompt 2 — make/order/buy/borrow router template

> I have a home shop with a handheld router, drill press, jigsaw,
> flush-trim bits, and clamps. I need to make eight matching ash chair
> arms with a sweeping outside curve. Help me decide whether I should
> make a router template, order one, buy a commercial template, or
> borrow shop tooling. I care more about repeatability than speed.

Expected: explicit make/order/buy/borrow recommendation with reuse,
lead-time, accuracy, shop-capability tradeoffs.

Observed: `spaces/home-shop-default/profile.yaml` loads (the SKILL.md
"omitted shop context" path now actually has a file to read). MOBOB
output (`references/make-order-buy-borrow.md`) recommends "make" with
trace → rough-cut → flush-trim sequence and a first-article template
check. Pass.

### Prompt 3 — laser carrier fixture + safety review

> I'm laser-cutting a batch of acrylic spacers at Maker Nexus and need
> a carrier fixture so small parts don't shift after the final contour
> cut. I also need a quick safety review because the stock comes with
> protective film and I want to avoid flare-ups. Give me the
> repeatable shop packet.

Expected: compact packet shape, fixture concept + workholding logic +
laser-specific safety + sourcing decision.

Observed: stays inside the compact `repeatable-shop-packets.md` shape;
carrier/window-frame retention; `safety-checklist.md` covers film flare,
air-assist dependence, stop-work conditions; sourcing leans
make-locally. Pass.

All three pass. None of the three regressed relative to the round-1 run
(same prompts, narrower contract).

## Recommendations for keeping the snapshot synced

1. **Run `scripts/sync_makerspace_snapshot.sh /path/to/standalone/makerspace`
   before each cross-platform release** of `claude-skills`. The script
   `rsync`s only the whitelisted directories
   (`SKILL.md manifest.yaml agents references assets spaces scripts examples evals`)
   and refuses to ship `catalog.sqlite`, `__pycache__`, or
   `evals/workspace/`.
2. **Hand-update `skills/makerspace/SOURCE_COMMIT.md`** with the
   standalone HEAD SHA the script prints, plus a note about any
   uncommitted working-tree drift (the 2026-05-08 snapshot includes such
   drift; the next snapshot should be cut from a clean SHA).
3. **Land the round-1 working-tree changes back in standalone `main`**
   so the next snapshot can be reproduced from a committed SHA without
   a footnote.
4. **When the standalone repo's `evals/workspace/` is rerun**, mirror
   the new iteration into `docs/benchmarks/makerspace/iteration-N/` in
   this repo (the sync script intentionally excludes `workspace/` so
   that move happens deliberately, not by accident).
5. **`scripts/` portability caveat**: the bundled scripts depend on
   local `sqlite` and a `spaces/` tree on disk. They are not expected
   to run inside Cowork/mobile installs, only on a host that has the
   standalone repo's data. They ship for reference and for use on the
   host machine.
6. **Sprint-manager note**: when running multiple cross-platform-review
   handoffs in parallel, give each agent a separate `git worktree add`
   under `/tmp/`. Six concurrent codex sessions on the same working
   tree will checkout-stomp each other's edits (this happened during
   round-2 — recovered by switching to an isolated worktree).
7. **Host-only annotations** (this file, future cross-platform-review
   docs) are protected from `--delete` by an explicit rsync filter for
   `evals/round-*-cross-platform-*.md` in the sync script. Name new
   host-only eval annotations to match that pattern, or extend
   `PROTECT_EVALS` in `scripts/sync_makerspace_snapshot.sh`.

## Self-consistency for portable installs

`evals/evals.json` no longer contains a `legacy_workspace` pointer that
escapes the package. The skill is now self-consistent under zip-upload
and mobile installs: nothing inside `skills/makerspace/` resolves to a
path outside the skill at runtime. The host-repo benchmark location is
still discoverable via the `legacy_workspace_note` description string,
which is human-readable context rather than a load instruction.
