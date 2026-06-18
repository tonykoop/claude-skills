# Autonomous-Sprint Governance Layer

Back-end guardrails for the multi-agent sprint system (Epic
[#254](https://github.com/tonykoop/claude-skills/issues/254)). One human acts as
**Chief Auditor** — verifying via automation, not eyeballs. Stand these up
*before* launching the tmux squads.

| Story | What it enforces | Module |
| --- | --- | --- |
| [#259](https://github.com/tonykoop/claude-skills/issues/259) | Least-privilege tool/secret scopes + spend dead-man's switch | `spend_guard.py` |
| [#256](https://github.com/tonykoop/claude-skills/issues/256) | Adversarial QA: never let a model audit its own asset | `review_router.py` |

Everything is driven by one config — [`agent-roster.yaml`](agent-roster.yaml) —
so the rules live in the orchestration config, not in any agent's prompt.

## #259 — Spend guard & least-privilege scopes

Two surfaces:

**Least-privilege scoping** is default-deny. Each agent inherits its
department's `allow_tools` / `allow_secrets`; `deny_*` always wins. The
studio-video (YouTube) agents get the YouTube API and never the local
filesystem or a repo token.

```python
from spend_guard import load_roster, scope_check
roster = load_roster()
scope_check(roster, "cindy", tool="youtube_api").allowed      # True
scope_check(roster, "cindy", tool="local_filesystem").allowed # False
```

**Maximizer-Mode dead-man's switch** evaluates a usage ledger:

- ≥ cap → `HARD_CAP` (halt the agent for the day)
- ≥ 75% of cap → `SOFT_WARN` (pause the heartbeat for audit)
- stale / missing ledger → **fail closed**, every agent `STALE`
- optional org-wide ceiling → `GLOBAL_CAP` blocks all dispatch

```console
$ python spend_guard.py --ledger usage.json
```

Exit code is non-zero whenever any agent is paused/halted or the ledger is
stale — wire it into the squad-launch preflight so a broken loop can't drain a
Max-tier budget overnight.

`usage.json` shape:

```json
{
  "generated_at": "2026-06-17T20:00:00Z",
  "agents": { "alice": {"spent_usd": 12.5}, "cindy": {"spent_usd": 3.0} }
}
```

## #256 — Adversarial cross-model review gate

The generating agent never verifies its own work; assets route to a QA Auditor
on a **distinct model family** (family-level, so a version bump can't re-enable
self-review).

```console
# pick an auditor for a fresh asset
$ python review_router.py assign --asset asset.json
# gate an existing creator->auditor handoff (merge gate)
$ python review_router.py validate --handoff handoff.json
```

Full walkthrough: [`examples/creator-auditor-handoff.md`](examples/creator-auditor-handoff.md).

## Config resolution

Both modules resolve `agent-roster.yaml` in this order (first match wins):

1. `$AGENT_ROSTER_CONFIG`
2. `~/.claude/agent-roster.yaml`
3. `governance/agent-roster.yaml` (the safe defaults in this repo)

## Tests

```console
$ pip install pyyaml pytest
$ pytest governance/tests -q
```

## Wiring into the sprint

- **Preflight (before `tmux-sprint` launch):** run `spend_guard.py --ledger …`;
  abort the launch on a non-zero exit.
- **Per-agent boot:** pass the agent its department scope; the launcher refuses
  to export a secret that fails `scope_check`.
- **Review hop:** `tmux-sprint` / `sprint-supervisor` call
  `review_router.assign` to pick the auditor and `validate_handoff` as the
  merge gate, replacing same-model self-review.
