# Provider Failover Contract

Issue: https://github.com/tonykoop/claude-skills/issues/166

This is the first implementation contract for migrating a budget-exhausted
sprinter pane from one CLI provider to another without abandoning the lane.
It is intentionally manager-owned: `sprint-supervisor` can approve safe prompt
shapes, but it should not decide provider routing.

> **Implementation status.** The "Low-Risk First PR Boundary" slice (below) is
> implemented in [`../scripts/provider_failover.py`](../scripts/provider_failover.py)
> with tests in [`../tests/test_provider_failover.py`](../tests/test_provider_failover.py):
> config parsing, exhaustion detection from a pane capture, the round-state
> provider record, next-provider selection, and the morning-summary table — all
> **detection/state only, no pane keystrokes**. The same-pane CLI swap
> (`C-c` / exit / relaunch / probe) is the follow-up PR that builds on this.

## Goals

- Keep the pane, worktree, assignment, and lane identity stable.
- Change only the backing provider/runtime when the current provider is
  exhausted or unavailable.
- Persist enough state that a compacted or replacement manager can see which
  panes migrated and why.
- Fall back to manager absorption only after all configured providers fail.

## Default Fallback Order

```yaml
provider_failover:
  order:
    - codex
    - claude
    - gemini
    - manager-absorb
  probe_prompt: "Say READY and exit."
  probe_success_pattern: "\\bREADY\\b"
  launch_timeout_seconds: 20
  probe_timeout_seconds: 30
```

The manager should treat this as configurable. A round may override the order
when the user explicitly requests a runtime mix or when a provider is known to
be unauthenticated on the host.

## Provider State

Round-state JSON should maintain a provider table keyed by pane or persona.
The minimum useful shape is:

```json
{
  "pane": "sprint:0.3",
  "persona": "dan",
  "lane": "core4-1511",
  "worktree": "/home/tony/wrfcoin/worktrees/core4-dan-1511",
  "provider": "claude",
  "provider_status": "available",
  "previous_provider": "codex",
  "failure_reason": "weekly_budget_exhausted",
  "last_migrated_at": "2026-05-17T12:34:56-07:00",
  "probe": {
    "prompt": "Say READY and exit.",
    "success": true,
    "output_excerpt": "READY"
  }
}
```

Suggested `provider_status` values:

- `available`
- `working`
- `exhausted`
- `auth_blocked`
- `probe_failed`
- `manager_absorbed`
- `unknown`

Suggested `failure_reason` values:

- `rate_limit_prompt`
- `weekly_budget_exhausted`
- `provider_cli_missing`
- `provider_auth_blocked`
- `probe_timeout`
- `launch_timeout`
- `manual_override`

## Exhaustion Signals

The manager should consider failover when pane capture shows one of these
families:

- codex weekly budget exhaustion or a weekly quota prompt
- codex rate-limit prompt that blocks useful progress
- provider-specific "no credits", "quota exceeded", or "usage limit" text
- repeated provider overload where retrying the same provider has already
  failed this round

Transient command approval prompts, local test failures, and ordinary context
compaction are not provider exhaustion. They should continue through the
existing supervisor, restart, or dispatch flows.

## Same-Pane Swap Flow

1. Capture the last 80 lines from the target pane and write the excerpt into
   the round-state failure record.
2. Mark the pane `exhausted` with the current provider and failure reason.
3. Send `C-c` once. If the provider does not return to an interactive prompt,
   send one more `C-c` after a short delay.
4. Exit the provider CLI without closing the tmux pane. Prefer the CLI's normal
   exit command when available; otherwise send `exit` at the shell prompt.
5. Confirm the pane is at a shell prompt or otherwise ready for a new process.
6. Launch the next configured provider in the same pane.
7. Send the availability probe: `Say READY and exit.`
8. If the probe succeeds, update the provider table and resume dispatching the
   original assignment to that pane.
9. If launch, auth, or probe fails, record the failure and try the next
   provider.
10. If every provider fails, mark the lane `manager_absorbed` and continue with
    the existing manager-absorption fallback.

## Provider Launch Commands

The public package should not assume every host has every CLI installed. Before
the first migration in a round, the manager should verify the configured
commands with `command -v`.

| Provider | Launch command | Success hint |
|---|---|---|
| `codex` | `codex` | Codex banner or model/status footer |
| `claude` | `claude` | Claude prompt/statusline |
| `gemini` | `gemini` | Gemini prompt/statusline |
| `manager-absorb` | no pane launch | lane reassigned to manager context |

Missing binaries are `provider_cli_missing`, not lane failures.

## Dispatch And Summary Integration

After a successful migration, the next dispatch record should keep the same
lane/persona assignment and only update the runtime/provider fields. The
manager should add a morning-summary section:

```markdown
## Provider Failover

| Pane | Persona | From | To | Reason | Probe | Result |
|---|---|---|---|---|---|---|
| sprint:0.3 | dan | codex | claude | weekly_budget_exhausted | READY | resumed |
```

If the lane was manager-absorbed, the summary should say which providers were
attempted and give the exact blocker for each.

## Low-Risk First PR Boundary

The first implementation PR should avoid broad tmux rewrites. A safe slice is:

- add config parsing for `provider_failover.order`
- add provider table serialization to round-state JSON
- add detection for exhaustion prompt families in preflight output
- report `FAILOVER_CANDIDATE` without sending any pane keystrokes

The pane-CLI swap can land only after that detection/state slice is validated
against saved pane-capture fixtures.

## Cost Economics

The verification task from the issue: *is this worth it on $ alone, or is the
real constraint per-provider quota?*

The dominant constraint is **per-provider weekly quota, not marginal dollars.**
The 2026-05-12 incident was panes hitting a *weekly* gpt-5.5 budget ~5 hours in,
while the host still had unused `claude` and `gemini` quota. Failover helps
regardless of per-token price because each provider carries an **independent
quota bucket**: moving an exhausted lane onto a fresh provider buys hours of
runway that no amount of price optimisation on the exhausted provider could.

Implications for the order:

- Order by **remaining quota and authentication state**, not by cheapest token.
  A cheaper provider that is already exhausted or unauthenticated is worth
  nothing this round.
- `manager-absorb` stays last because it concentrates load on one context — the
  exact fragility this feature exists to avoid.
- Per-token price is a tiebreaker only: among providers with quota left, prefer
  the cheaper one. It never overrides "has quota / is authenticated."

So the feature is justified by quota resilience first; dollar savings are a
secondary, order-tiebreaking concern.

## Using the detection slice

```console
# classify a captured pane and emit a round-state failover record
$ python3 scripts/provider_failover.py detect \
    --capture pane-capture.txt \
    --pane sprint:0.3 --persona dan --lane core4-1511 --provider codex
FAILOVER_CANDIDATE: pane sprint:0.3 (codex) -> claude  reason=weekly_budget_exhausted
  action: FAILOVER_CANDIDATE      # exit code 1 = candidate; 0 = healthy

# roll the recorded candidates into the morning summary
$ python3 scripts/provider_failover.py summary --records failover-records.json
```

`detect` exits 1 when a candidate is found so a manager loop can branch on the
exit code. Transient noise (approval prompts, local test failures, compaction)
is explicitly *not* treated as exhaustion and returns exit 0.
