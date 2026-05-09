# Issue Triage - 2026-05-09

Scope: reconcile currently open `claude-skills` issues against `origin/main`
after recent merged PRs #19-#25. This note is intentionally advisory only:
no issues were closed and no PRs were merged by this agent.

## Recommended Manager Actions

### Close as Complete

| Issue | Evidence | Recommended action |
|---|---|---|
| #3 `[infra] Maintain canonical manifest.yaml for skill versions` | `manifest.yaml` now has `schema_version`, `last_updated`, `install_roots`, 14 active `skills` entries, and separate `planned_skills.energy-management`; each active entry includes `canonical_version`, `runtime`, `repo_path`, `last_updated`, and `status`. | Close as complete for the current schema. Open a follow-up only when the schema needs a new consumer-driven field. |
| #4 `[infra] Define skills-meta drift audit requirements` | `skills/skills-meta/references/manifest-schema.md` defines inventory fields, comparison rules, and frontmatter-fix output; `docs/skill-versioning.md` has the drift-check list; PR #21 shipped unreadable-root, duplicate, JSON, and fix modes. | Close after linking PR #21 and #18 as implementation evidence. |
| #9 `[new-skill] Build idea-incubator skill` | `skills/idea-incubator/` exists with `SKILL.md`, references, agents file, label bootstrap scripts, changelog, evals, and manifest entry `idea-incubator` at `1.1.0`; PR #23 handled cross-platform follow-up. | Close as complete. |
| #13 `[new-skill] Build yoga-sequencer skill` | `skills/yoga-sequencer/` exists with references, evals, agents file, and manifest entry; PR #19 merged lazy-load and portable playlist handoff work. Follow-ups #26 and #27 now cover the remaining yoga refinements. | Close as complete, leaving #26 and #27 open. |
| #14 `[new-skill] Build maker-engineering umbrella routing skill` | `skills/maker-engineering/` exists with routing tree, DoE template, specialist registry, evals, and manifest entry; PR #22 fixed canonical specialist naming and runtime-agnostic handoffs. | Close as complete. |
| #15 `[new-skill] Build makerspace fabrication specialist skill` | `skills/makerspace/` exists with references, specialists, shop profiles, scripts, examples, evals, manifest, `SOURCE_COMMIT.md`, and manifest entry; PR #24 made the portable snapshot self-contained and moved heavy benchmarks to `docs/benchmarks/makerspace/`. | Close as complete. |
| #17 `[new-skill] Build reverse-engineer analysis skill` | `skills/reverse-engineer/` exists with uncertainty references, builder handoff template, measurement checklist, agents file, evals, and manifest entry; PR #20 added no-vision intake and sync documentation. | Close as complete. |
| #18 `[new-skill] Build skills-meta skill from handoff` | `skills/skills-meta/` exists with `SKILL.md`, manifest schema, output examples, runtime roots, helper script, tests, evals, and manifest entry; PR #21 added the cross-platform behavior that made it usable against current repo state. | Close as complete. |

### Keep Open / Good Next PRs

| Issue | Evidence | Recommended action |
|---|---|---|
| #1 `[infra] Add per-skill CHANGELOG.md files` | Only `skills/idea-incubator/CHANGELOG.md` is present as a per-skill changelog on `origin/main`; most active skill directories still lack one. | Keep open. Good low-risk PR: add changelog stubs for all active skills and document the entry convention. |
| #2 `[infra] Tag skill releases before packaging and upload` | `docs/skill-versioning.md` documents tag format and workflow, but the repo has no tags yet and no automated release artifact path. | Keep open. Next PR should create the first tag plan and decide whether tags wait until #1/#5/#6 land. |
| #5 `[workflow] Add repeatable skill packaging scripts` | `scripts/validate_packaged_paths.py` and `scripts/sync_makerspace_snapshot.sh` help packaging safety, but there is no generic package-by-name script that reads `manifest.yaml`, checks dirty state, builds from a tag/current checkout, and emits versioned zip names. | Keep open. Good next PR candidate, especially before any public or mobile install round. |
| #7 `[tmux-v3] Align tmux sprint skill with canonical skill ecosystem controls` | PR #25 added worktree and rename protocol to `codex/skills/tmux-v2`, but #7 asks for the broader tmux-v3 roadmap: external roadmap links, canonical metadata, adapters, hooks/routines, and benchmark cases. | Keep open. Treat PR #25 as supporting evidence, not completion. |
| #8 `[controls] Define skill activation, routing, conflicts, and deprecation` | `docs/skill-controls.md` establishes the control surfaces, but it is still high-level and does not yet define detailed overlap resolution, deprecation metadata/removal workflow, or the precise `SKILL.md` versus references/scripts/assets boundary. | Keep open. Good next PR: expand `docs/skill-controls.md` into an operational checklist. |
| #10 `[public] Public release readiness sweep` | `docs/public-release-checklist.md` exists and README is now public-oriented, but the checklist still has unchecked gates and the repo still contains private paths and WRFCoin provenance by design. | Keep open until the actual scrub is performed. |
| #11 `[benchmark] Add skill benchmark harness and run logs` | `docs/benchmarking.md` defines the benchmark shape and `docs/benchmarks/makerspace/` stores real artifacts, but there is not yet a generic harness with fixture format, run-log format, and sample benchmarks for `tmux-v2`, `skill-creator`, and one planned skill. | Keep open. Good next PR after #5 or alongside it. |
| #12 `[workflow] Add cross-device skill sync and check workflow` | `manifest.yaml` now has `install_roots`, and `skills-meta` documents runtime roots/unreadable roots, but there is no concise repo-to-tagged-zip-to-install checklist per runtime yet. | Keep open. Good next PR: add a `docs/cross-device-sync.md` checklist and link it from `skills-meta`. |
| #16 `[new-skill] Explore energy-management skill` | `manifest.yaml` lists `planned_skills.energy-management`, but no `skills/energy-management/` exists and the issue explicitly asks to validate skill versus template first. | Keep open as discovery, not implementation debt. |
| #26 `[yoga-sequencer] Tighten staple-pose cheat-sheet safety boundaries` | Opened after PR #19. The request is a targeted safety refinement to split safe default staples from constraint-sensitive staples that require `poses.yaml`. | Keep open. Good small PR candidate in `skills/yoga-sequencer/SKILL.md`. |
| #27 `[yoga-sequencer] Add shorter-class playlist handoff worked examples` | Opened after PR #19. Current `references/playlist-builder-handoff.md` has portable YAML guidance, but the issue asks for explicit 45-minute and ideally 30-minute examples. | Keep open. Good small PR candidate in `skills/yoga-sequencer/references/playlist-builder-handoff.md`. |

### Blocked / Needs Policy Decision

| Issue | Evidence | Recommended action |
|---|---|---|
| #6 `[infra] Add version and last-updated frontmatter to every SKILL.md` | `docs/skill-versioning.md` says the target frontmatter includes `version` and `last-updated`, but also records a current compatibility constraint: the bundled `skill-creator` validator accepts only `name` and `description`. `git grep` found no `version:` fields in `*SKILL.md` on `origin/main`, while `manifest.yaml` carries canonical versions. | Keep open but mark blocked on validator/policy. Manager should decide whether to update the validator to allow version fields or revise #6 to make manifest-only metadata acceptable for now. |

## Suggested Queue

1. Close the completed build issues: #3, #4, #9, #13, #14, #15, #17, #18.
2. Assign small yoga follow-ups next: #26 and #27.
3. Decide the metadata policy for #6 before investing heavily in #1, #2, or
   #5, because changelog, tags, packaging, and drift checks all depend on the
   same source-of-truth convention.
4. Batch the remaining infra work as a release-readiness lane: #1, #2, #5,
   #8, #10, #11, #12, with #7 as the tmux-v3 bridge and #16 as separate
   discovery.
