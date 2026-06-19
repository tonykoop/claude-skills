# Worked example — circuit-breaker verdicts

Satisfies the claude-skills#258 acceptance criteria: confidence-threshold
auto-advance vs. escalate, escalation that pings the human only for ambiguous
cases, and a hard rule that no agent crosses a deploy boundary without a manual
signature.

The breaker runs *after* the #256 cross-model audit. Its input is a verdict
record: the same creator→auditor handoff plus the auditor's `confidence`, the
`linters_passed` flag, and the `action` / `target_branch` being gated.

## 1 — The easy 90%: high confidence, non-protected → auto-advance

`frank` (spark) wrote a URDF fix; `alice` (opus) audited it cross-model and is
confident.

`verdict.json`:

```json
{
  "asset_id": "robotics/urdf-knee-fix-001",
  "creator_agent": "frank", "creator_model": "gpt-5.3-codex-spark",
  "auditor_agent": "alice", "auditor_model": "claude-opus-4-8",
  "linters_passed": true,
  "confidence": 0.96,
  "action": "merge_pr",
  "target_branch": "feature/knee-fix",
  "human_signature": null
}
```

```console
$ python circuit_breaker.py decide --verdict verdict.json ; echo "exit=$?"
Circuit-breaker verdict: AUTO_ADVANCE
  - confidence 0.96 >= bar 0.90 and linters passed
exit=0
```

No human is paged. This is the case the org wants to be automatic.

## 2 — The ambiguous ~10%: low confidence → escalate (ping the human)

Same handoff, but the auditor is only `0.62` confident.

```console
$ python circuit_breaker.py decide --verdict low.json ; echo "exit=$?"
Circuit-breaker verdict: ESCALATE
  - confidence 0.62 < bar 0.90 — ambiguous, human reviews
  >> PING @tonykoop: low confidence (0.62 < 0.90) (asset robotics/ambiguous-002)
exit=1
```

A linter failure escalates the same way, regardless of confidence — the human's
scarce hours go only to the genuinely hard cases.

## 3 — The hard rule: a deploy boundary is never crossed unattended

Even at **confidence 1.0** with clean linters, an action that touches `main`
(or `publish` / `deploy` / `release`) is blocked pending a human signature.

```json
{
  "asset_id": "robotics/deploy-001",
  "creator_agent": "frank", "creator_model": "gpt-5.3-codex-spark",
  "auditor_agent": "alice", "auditor_model": "claude-opus-4-8",
  "linters_passed": true, "confidence": 1.0,
  "action": "push_main", "target_branch": "main",
  "human_signature": null
}
```

```console
$ python circuit_breaker.py decide --verdict deploy.json ; echo "exit=$?"
Circuit-breaker verdict: BLOCK
  - protected action 'push_main' / branch 'main' — human signature required (confidence 1.0 cannot override)
  >> PING @tonykoop: deploy boundary — manual signoff required (asset robotics/deploy-001)
exit=1
```

The protected floor is **hardcoded** in `circuit_breaker.py`
(`IMMUTABLE_PROTECTED_ACTIONS` / `IMMUTABLE_PROTECTED_BRANCHES`). Emptying
`protected_actions` / `protected_branches` in `agent-roster.yaml` — or even
setting `circuit_breaker.enabled: false` — cannot let an agent push `main`.

## 4 — Human signs off → the barrier releases

A human (out-of-band) populates `human_signature`. Only then does the protected
action advance:

```json
{ "...": "...", "action": "push_main", "target_branch": "main",
  "human_signature": {"signed_by": "tony", "at": "2026-06-17T21:00:00Z"} }
```

```console
$ python circuit_breaker.py decide --verdict signed.json ; echo "exit=$?"
Circuit-breaker verdict: AUTO_ADVANCE
  - protected action carries a valid human signature
exit=0
```

## 5 — Untrustworthy audit can't be rescued by a high score

If the upstream handoff is self-review or same-family (the #256 gate would
reject it), its confidence is meaningless and the breaker escalates regardless:

```json
{ "creator_agent": "alice", "creator_model": "claude-opus-4-8",
  "auditor_agent": "alice", "auditor_model": "claude-opus-4-8",
  "linters_passed": true, "confidence": 1.0,
  "action": "merge_pr", "target_branch": "feature/x" }
```

```console
$ python circuit_breaker.py decide --verdict self.json ; echo "exit=$?"
Circuit-breaker verdict: ESCALATE
  - cross-model handoff invalid: self-review: creator and auditor are both 'alice'; same model family 'opus': ...
  >> PING @tonykoop: untrustworthy audit (handoff failed the QA gate) (asset ...)
exit=1
```

A non-zero exit is the gate's stop signal: the supervisor pings the human and
never advances on the breaker's behalf.
