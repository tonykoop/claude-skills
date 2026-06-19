# Worked example — automated verification gates → QA decision

Satisfies claude-skills#257: a headless runtime (not a human reading code)
decides whether work passes, and the **gate results attach to the QA decision**
that the #258 circuit breaker reads.

Three gates ship in [`verification_gates.py`](../verification_gates.py):

| Gate | Domain | Catches |
| --- | --- | --- |
| `sandbox-exec` | cross | runtime errors: exceptions, syntax errors, non-zero exit, hangs |
| `markdown-length` | studio | stub/runaway scripts, missing headings, broken fences, long lines |
| `urdf-joint-limit` | robotics | joints with no `<limit>`, degenerate ranges, bad effort/velocity, home pose out of range |

## 1 — Sandbox execution gate

```console
$ cat > sol.py <<'PY'
def fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a
assert fib(10) == 55
PY
$ python verification_gates.py sandbox --file sol.py
[PASS] sandbox-exec (cross): sol.py executed cleanly (exit 0)
------------------------------------------------
ALL GATES PASSED
```

A bug fails it — the machine catches it, not a reviewer:

```console
$ printf 'raise ValueError("boom")\n' > broken.py
$ python verification_gates.py sandbox --file broken.py ; echo "exit=$?"
[FAIL] sandbox-exec (cross): broken.py raised a runtime error (exit 1)
        - ValueError: boom
------------------------------------------------
BLOCKED: sandbox-exec
exit=1
```

The script runs in a throwaway working directory with a wall-clock timeout, so a
relative read of the repo or an infinite loop both fail closed.

## 2 — Markdown / length linter (studio)

```console
$ python verification_gates.py markdown --file episode-script.md
[FAIL] markdown-length (studio): episode-script.md: 2 issue(s) (41 words)
        - too short: 41 words < 80 (looks like a stub)
        - no markdown heading (#) — script has no structure
------------------------------------------------
BLOCKED: markdown-length
```

## 3 — URDF joint-limit test (robotics)

```console
$ python verification_gates.py urdf --file left_leg.urdf \
    --home-positions '{"hip": 3.0}'
[FAIL] urdf-joint-limit (robotics): left_leg.urdf: 1 joint-limit issue(s) across 2 actuated joint(s)
        - joint 'hip': home position 3.0 outside limit [-1.57, 1.57]
------------------------------------------------
BLOCKED: urdf-joint-limit
```

## 4 — Attaching to the QA decision

Run every artifact in one pass from a manifest and emit the QA-decision payload:

`artifacts.json`:

```json
{
  "artifacts": [
    {"gate": "sandbox", "language": "python", "path": "sol.py"},
    {"gate": "markdown", "path": "episode-script.md"},
    {"gate": "urdf", "path": "left_leg.urdf", "home_positions": {"hip": 0.5}}
  ]
}
```

```console
$ python verification_gates.py report --manifest artifacts.json --json
{
  "gates_passed": false,
  "failed_gates": ["markdown-length"],
  "gate_count": 3,
  "gates": [ ... per-gate results ... ]
}
```

The `gates_passed` / `failed_gates` keys are the stable contract the
human-in-the-loop circuit breaker (claude-skills#258) reads: linters-pass is a
precondition for confidence-based auto-advance, and any failed gate forces the
ticket to escalate.
