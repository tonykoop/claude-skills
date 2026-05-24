# Operational Judgment Benchmarks

Use this pattern for skills whose value is the quality of a decision rather
than the polish of a generated artifact. It is an initial regression-detection
pattern for operational skills such as `sprint-supervisor`; it does not claim
to prove live operational readiness.

## What To Benchmark

Start from the skill's explicit decision surface:

- rubric coverage: each approval row has at least one fixture;
- refusal-list adherence: each hard-stop class has a fixture over time;
- escalation timing: fixtures distinguish "handle locally" from "wake user";
- summary completeness: end-of-run summaries retain required caveats;
- scope discipline: multi-supervisor or worktree boundaries are preserved.

For `sprint-supervisor`, the first surface is the approval rubric, refusal
list, escalation triggers, and morning-summary contract in its `SKILL.md`.

## Fixture Shape

Each case should be a small archived scenario, not a live tmux run:

- `capture.txt`: synthesized or archived `tmux capture-pane` tail;
- `expected-decision.md`: the expected action and why;
- optional `notes.md`: provenance, known ambiguity, or baseline notes.

Keep fixture text realistic enough to exercise the prompt shape. Avoid
embedding secrets, private repo paths beyond the minimum needed for the
decision, or live host state that would make the fixture age poorly.

## Scoring

Prefer simple, reviewable assertions before model-in-the-loop grading:

- expected action appears: approve, refuse, escalate, preserve model, summarize;
- rationale cites the governing rubric row or refusal trigger;
- unsafe alternatives are absent, such as "auto-approved" for hard-stop cases;
- summary cases include both work completed and caveats.

These checks are intentionally coarse. They catch regressions in decision shape
and vocabulary; they do not replace live supervision or human review.

## Baselines

When comparing with-skill and without-skill runs, archive both candidates with
the same fixture text and runtime label. Score the same watch-points across
both runs. Report the delta as evidence for a PR, not as a universal model
ranking.

## Review Rules

- Treat passes as "fixture-compatible", not "operationally safe".
- Add a new fixture whenever the skill gains a rubric row, refusal trigger, or
  summary obligation.
- Keep benchmark suites runnable without network access, live tmux sessions, or
  current GitHub state.
- Use `Refs #...` posture for methodology slices unless the issue is fully and
  narrowly closed.

