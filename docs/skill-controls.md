# Skill Controls

Skill controls are the rules and tools that prevent a growing skill ecosystem
from becoming a pile of prompt fragments. They keep activation predictable,
routing crisp, deprecation safe, and runtime behavior aligned across Claude,
Codex, Gemini, and future desktop or automation variants.

## Control Surfaces

- Activation: precise frontmatter descriptions and trigger phrases.
- Routing: umbrella skills route; specialist skills do the work.
- Conflict handling: overlapping triggers are resolved by precedence rules, not by guesswork.
- Versioning: every skill has structured version metadata.
- Packaging: zips are built from tagged commits.
- Drift detection: installed versions are checked against `manifest.yaml`.
- Deprecation: old skills remain documented and discoverable until removed from every device.
- Runtime parity: the same skill behaves the same way across runtimes, or the difference is documented.
- Benchmarking: fragile skills get repeatable test prompts and watch-points.
- Review gates: every skill PR carries evidence for static, behavior, runtime,
  and regression review before it is merged.

---

## Activation: Trigger Precedence

A skill activates when the runtime decides the user's intent matches its
`description`. The description is the only field guaranteed to be read at
activation time across runtimes, so it carries the entire activation contract.

When two or more skills could plausibly match, the runtime should prefer them
in this order:

1. **Explicit invocation.** The user typed `/<skill-name>` or named the skill.
2. **Specialist over umbrella.** If a specialist skill's description matches
   the request directly, prefer it over an umbrella router.
3. **Narrowest scope.** Prefer the skill whose description names the specific
   artifact, file type, or action being requested over one that names a
   broader category.
4. **Highest canonical version.** When two skills have the same scope, prefer
   the one whose `manifest.yaml` entry is `status: active` and has the higher
   `canonical_version`.
5. **Runtime-native.** If a `runtime: portable` skill and a runtime-specific
   skill (`runtime: claude`, `runtime: codex`, `runtime: gemini`) both match,
   prefer the runtime-specific skill on its native runtime; prefer the
   portable skill elsewhere.
6. **Most recently updated.** Tie-breaker only. Use `last_updated` from the
   manifest.

Skills that do not want to compete in step 2 or 3 should say so in their
description (`Do not use for ...`, `Prefer <other-skill> when ...`).

### Description Hygiene

- Lead with the verbs and nouns a user would actually type.
- Include both the request shape ("design a jig") and the artifact shape
  ("STL", "BOM", "shop packet").
- Add an explicit `Do not use for ...` clause when the skill is adjacent to
  a more specific specialist.
- Avoid project-only jargon. Examples that mention private projects must be
  generic enough to make sense to a reader who has never seen them.

---

## Routing: Umbrella vs Specialist

An **umbrella skill** triages, clarifies, and hands off. A **specialist
skill** owns a deliverable.

Use an umbrella skill when:

- The user's request spans multiple specialist domains.
- The right specialist is ambiguous and a clarifying question is cheaper than guessing.
- The work is early-stage and needs scoping before any artifact is produced.
- A specialist needs structured intake (a design table, a DoE plan, a problem framing).

Use a specialist skill directly when:

- The request names a specific artifact the specialist owns end-to-end.
- One specialist clearly owns the whole task with no scope leakage.
- The user has already done triage, manually or in a previous turn.

Routing rules every umbrella should follow:

1. **Hand off, don't impersonate.** The umbrella may produce intake notes,
   problem framing, and a handoff document, but it must not produce the
   specialist's primary artifact.
2. **Name the specialist by canonical name.** Use the name from
   `manifest.yaml`, not a versioned alias. Versioned aliases (e.g.
   `instrument-maker-v4`) drift; canonical names route reliably across
   runtimes.
3. **State the handoff explicitly.** Tell the user which specialist will own
   what, and what the umbrella is producing for them.
4. **Refuse to overreach.** If no specialist matches, say so and offer to
   incubate the idea or escalate.

Example (portable, illustrative): an umbrella for physical-making intake
should route requests for "design a flute" to an instrument specialist,
"build a jig" to a fabrication specialist, and "what is this part" to a
reverse-engineering specialist, while keeping early-stage idea framing
inside the umbrella itself.

---

## Conflict Handling: Overlapping Triggers

Trigger collisions are inevitable as the catalog grows. Resolve them with
this hierarchy:

1. **Schema first.** Run the description through the activation precedence
   above. The intended winner should be unambiguous on paper.
2. **If two skills still tie**, treat it as a control bug, not a runtime
   bug. Fix one of the descriptions:
   - Tighten the loser's scope (`Do not use for X`, `Prefer Y when Z`).
   - Or merge the two skills if they truly overlap.
3. **If the overlap is intentional** (e.g. a portable skill and a runtime
   adapter), document the relationship in both descriptions and in
   `manifest.yaml` notes. The adapter's description should reference the
   portable skill by name.
4. **If the overlap is temporary** (e.g. v2 and v3 of the same skill exist
   side-by-side during migration), mark the older one `status: deprecated`
   in the manifest and add a `Prefer <newer>` clause to its description.

A trigger collision that survives a release is a release blocker. Add a
benchmark prompt that exercises both skills' descriptions to lock in the
intended winner.

---

## Review Gate

Every skill, runtime adapter, command, hook, or benchmark PR should link to the
agentic skill gate in `docs/review-gates/agentic-skill.md` and include the PR
evidence contract from `docs/review-gates/pr-evidence-contract.md`.

The gate is intentionally staged:

1. **Static:** frontmatter, description, manifest, changelog, references,
   scripts, and public-safety hygiene are internally consistent.
2. **Behavior:** trigger, non-trigger, ambiguity, conflict, and safety/deprecation
   fixture prompts prove the routing claim.
3. **Runtime:** tested runtimes, permission/settings needs, hooks, and adapter
   determinism are stated.
4. **Regression:** adjacent skills, deprecated versions, public examples, and
   benchmark coverage do not drift.

Missing evidence is a changes-requested finding even when the implementation
looks plausible.

---

## Deprecation Behavior

Skills are deprecated, not silently removed. The lifecycle is:

| Status | Meaning | Discoverable | Activates |
|---|---|---|---|
| `active` | Current canonical version. | yes | yes |
| `deprecated` | Replaced or retired; kept for migration. | yes | yes, with warning |
| `archived` | Out of rotation; preserved for history only. | yes (in manifest) | no |
| `removed` | Deleted from manifest after every install has migrated. | no | no |

Deprecation metadata in `manifest.yaml`:

```yaml
example-old-skill:
  canonical_version: 1.4.0
  runtime: portable
  repo_path: skills/example-old-skill
  status: deprecated
  deprecated_on: 2026-05-08
  superseded_by: example-new-skill
  remove_after: 2026-08-08
  notes: Migration guide in CHANGELOG.md.
```

Behavior expectations:

- A `deprecated` skill must keep working. Breaking it before `remove_after`
  defeats the purpose of deprecation.
- The skill's `description` must add a `Deprecated: prefer <successor>`
  clause so the runtime can route around it.
- The successor's description should mention the predecessor's name so
  searches and triggers carrying the old name still resolve.
- `remove_after` is advisory; do not delete until `skills-meta` (or the
  cross-device sync workflow) reports zero installed copies.
- Archived skills stay in the repo at their tagged commit so old packages
  remain reproducible.

---

## SKILL.md vs References, Scripts, Assets, and Repo Docs

Keep `SKILL.md` lean. Anything heavier belongs alongside it.

| Lives in | Use for |
|---|---|
| `SKILL.md` frontmatter | `name`, `description`, and (where the validator allows) `version`, `last-updated`. Trigger-critical only. |
| `SKILL.md` body | Scope, routing rules, the workflow steps the runtime must follow, brief examples. Aim for content the agent must read every activation. |
| `references/` | Long-form domain docs the agent should pull in only when needed. Linked from `SKILL.md` by name. |
| `scripts/` or `bin/` | Executable helpers invoked by the skill. Must be present when the skill ships. |
| `assets/` | Templates, schemas, fixtures, sample data, images. |
| `evals/` or `benchmarks/` | Activation, behavior, and regression prompts. |
| `CHANGELOG.md` (per skill) | Per-version history. |
| `docs/` (repo level) | Cross-skill policy: this file, versioning, architecture, public-release checklist. |
| `manifest.yaml` | Canonical version registry. The single source of truth for what is active. |

Rules:

- A `SKILL.md` should not embed long reference content the agent rarely needs.
  Move it to `references/` and link it.
- Bundled scripts referenced by `SKILL.md` must be present in the package.
  The public-release checklist enforces this.
- Repo-wide policy (this doc, versioning, release checklist) does not belong
  in any single `SKILL.md`. Skills may link to it but should not duplicate it.

---

## Runtime Parity

Preferred runtime targets:

- Claude Code and Claude Desktop.
- Codex and Codex Desktop.
- Gemini CLI and Gemini runtime.
- Future plugins, connectors, routines, hooks, and automations.

Where runtime-specific implementation lives:

- `claude/` — Claude Code skills, commands, hooks, routines.
- `codex/` — Codex skills and runtime ports.
- `gemini/` — Gemini parity, when added.
- `skills/` — Portable skill logic with no runtime dependency.

Parity expectations:

1. **Same name across runtimes.** A Claude adapter and a Codex adapter for
   the same logical skill share the canonical name in `manifest.yaml`.
   Differentiate by `runtime:` field, not by renaming.
2. **Same triggers across runtimes.** Activation behavior should not depend
   on the runtime unless the skill is explicitly runtime-specific (e.g. a
   tmux driver that only makes sense where tmux is available).
3. **Same outputs across runtimes.** If a skill produces a build packet on
   Claude, the Codex adapter must produce a build packet of the same shape.
4. **Document divergence.** Any place a runtime adapter cannot match the
   portable skill must call that out in `SKILL.md` and in the adapter's
   manifest entry.
5. **Adapter handoffs use the canonical name.** A Claude skill that hands
   off to Codex (or vice versa) should reference the target by canonical
   name and rely on the runtime to resolve the adapter.

Runtime adapters that wrap a portable skill should keep their own logic
thin: invocation, runtime-specific I/O, and any shell/tmux/connector glue.
Domain logic stays in the portable skill.

---

## Public Release Gate

Before public release, each skill should be reviewed for:

- personal paths and secrets;
- private project assumptions that need project-neutral wording;
- private repo names or operational details that should be generalized;
- bundled resources that are missing from the repo;
- deterministic setup instructions;
- benchmark or smoke-test coverage;
- examples that are clearly marked as examples when they reference a
  specific project.

Examples in a skill are allowed to be project-specific when they are clearly
labeled as illustrative ("Example, illustrative:"). Examples that look like
required configuration but assume a private project must be generalized
before release. The detailed checklist lives in
[public-release-checklist.md](public-release-checklist.md).

---

## Open Policy Questions

These are intentionally unresolved and tracked for follow-up:

- **Trigger benchmarking.** What is the minimum set of activation prompts a
  skill must pass before release? `docs/benchmarking.md` should encode it.
- **Cross-device sync semantics.** When a deprecated skill is still installed
  on a desktop client, does the manifest reclaim that as drift or as a
  permitted lag window? Tracked alongside the planned cross-device sync
  workflow.
- **Runtime adapter ownership.** When a portable skill changes shape, how
  long does an adapter have to catch up before it is marked `deprecated`?
- **Umbrella authority.** Should umbrella skills be allowed to refuse a
  handoff and ask the user to invoke the specialist directly, or should
  they always attempt routing? Current default is "attempt routing, refuse
  only when no specialist matches."
- **Trigger collision detection.** Should `skills-meta` flag descriptions
  whose embedding similarity exceeds a threshold, or rely on benchmark
  prompts as the only collision check?
