# Skill Benchmarking

The benchmark model is inspired by the instrument-maker benchmark suite:
fixed prompts, explicit watch-points, and run logs that make regressions visible.

## Benchmark Shape

Each benchmark should define:

- skill under test;
- runtime under test;
- prompt fixture;
- expected mode or route;
- expected artifacts;
- watch-points;
- pass/fail notes;
- manual interventions.

## Initial Watch-Points

- Trigger accuracy: the right skill activates.
- Routing accuracy: umbrella skills delegate rather than doing specialist work.
- Context discipline: the skill loads only needed references.
- Version awareness: the skill reports its own version when asked.
- Portability: output is not hard-coded to one project base.
- Handoff quality: generated issues/prompts are enough for another agent to act.

## Lightweight Harness

Use the repo-level harness for deterministic fixture checks before adding heavier
model-in-the-loop evaluation. The harness reads a JSON suite, checks archived
text/file artifacts, prints a short pass/fail summary, and can write a JSON run
log for PR review.

Sample command:

```bash
python3 scripts/skill_benchmark.py docs/benchmarks/sample-suite.json \
  --run-id sample-2026-05-09 \
  --created-at 2026-05-09T00:00:00Z \
  --out docs/benchmarks/run-logs/sample-maker-engineering-run.json
```

Expected summary:

```text
PASS sample-skills-platform-controls: 13/13 assertions across 4 case(s)
Wrote docs/benchmarks/run-logs/sample-maker-engineering-run.json
```

The checked-in sample suite validates maker-engineering, tmux-v2, skill-creator,
and planned-skill handoff fixtures without calling a model. For future
instrument-maker comparisons, add one case per prompt fixture and point each
`candidate.path` at the archived output directory for that runtime or skill
version. Keep generated run logs near the artifacts they grade, or archive them
under `docs/benchmarks/run-logs/` when the result supports a PR.

See [run-log-schema.md](benchmarks/run-log-schema.md) for the current output
format.

## Operational Judgment Benchmarks

Operational skills such as `sprint-supervisor` need a narrower benchmark shape
than artifact-producing skills. The first pass should check archived decision
fixtures: synthesized `tmux capture-pane` tails, expected approval/refusal or
summary decisions, and watch-points that map back to the skill's rubric. Treat
these as regression signals for judgment shape, not proof that a live
supervisor will make every correct call.

Run the static sprint-supervisor sample with:

```bash
python3 scripts/skill_benchmark.py docs/benchmarks/sprint-supervisor-judgment-suite.json \
  --run-id local-sprint-supervisor-judgment \
  --created-at 2026-05-23T00:00:00Z
```

The methodology lives in the `skills-meta` package reference
`references/operational-judgment-benchmarks.md` so future operational skills can
reuse the same fixture and scoring pattern.

## Known Gaps

- **No model-in-the-loop evaluation**: the harness checks static file/text
  fixtures only; it cannot verify that a live model run activates the right
  skill or produces correct output.
- **No CI integration**: the harness is invoked manually; automated gate on
  `scripts/skill_benchmark.py` is not yet wired into any CI workflow.
- **Response fixtures are hand-authored**: fixture files under
  `docs/benchmarks/fixtures/` capture expected output patterns; they are not
  recorded from real model runs and may drift as skills evolve.
- **Single suite, single runtime**: the sample suite covers one pass of four
  skills; cross-runtime (Codex CLI, Gemini CLI) and multi-version routing
  coverage is not yet included.
- **No regression baseline**: run logs are archived for reference but there is
  no automated comparison to a previous run; regressions surface only on
  manual inspection.
