# Worked example — creator → distinct-model auditor handoff

Satisfies the claude-skills#256 acceptance criterion: *"A worked example shows a
creator→auditor handoff."*

## Scenario

`alice` (department `robotics`, model `claude-opus-4-8`, family **opus**) finishes
a URDF kinematic patch for the humanoid-robotics repo. Under the old flat org she
would have re-read her own diff and merged it — a same-model blindspot. The
adversarial gate forbids that.

## Step 1 — asset emitted by the creator

`asset.json`:

```json
{
  "id": "robotics/urdf-knee-fix-001",
  "creator_agent": "alice",
  "creator_model": "claude-opus-4-8",
  "artifact_path": "robotics/urdf/left_leg.urdf.xacro"
}
```

## Step 2 — router assigns a distinct-family auditor

```console
$ python review_router.py assign --asset asset.json
{
  "ok": true,
  "auditor": "bob",
  "reason": "alice (opus) -> bob (haiku)"
}
```

The router skips `alice` (same agent) and any other **opus** agent, then takes
the first eligible distinct-family auditor in roster order — `bob` (model
`claude-haiku-4-5`, family **haiku**) — a genuinely different model, so the
audit cannot inherit the creator's bias. Selection is deterministic: the same
asset always routes to the same auditor. (The orchestrator may override with any
auditor the gate accepts — e.g. the cross-vendor `dan`/**gpt-5.5** — and the
`validate` gate below confirms that choice.)

## Step 3 — the handoff record

When `dan` accepts the work, the orchestrator writes a handoff record:

`handoff.json`:

```json
{
  "asset_id": "robotics/urdf-knee-fix-001",
  "creator_agent": "alice",
  "creator_model": "claude-opus-4-8",
  "auditor_agent": "dan",
  "auditor_model": "codex-gpt-5.5"
}
```

## Step 4 — gate validates the handoff before merge

```console
$ python review_router.py validate --handoff handoff.json
OK: handoff obeys adversarial-QA policy
```

## Counter-example — self-review is blocked

If the orchestrator (or a buggy loop) tries to route `alice`'s asset back to
`bob`-via-opus, or to `alice` herself:

```json
{
  "creator_agent": "alice", "creator_model": "claude-opus-4-8",
  "auditor_agent": "alice", "auditor_model": "claude-opus-4-8"
}
```

```console
$ python review_router.py validate --handoff self_review.json ; echo "exit=$?"
BLOCKED:
  - self-review: creator and auditor are both 'alice'
  - same model family 'opus': 'claude-opus-4-8' audited by 'claude-opus-4-8' — cross-model bias blindspot
exit=1
```

A non-zero exit code is the merge gate's stop signal.

## Same family, different version — still blocked

`claude-opus-4-6` auditing `claude-opus-4-8` is rejected because the comparison
is at the **family** level, so a routine version bump can never silently
re-enable self-review.
