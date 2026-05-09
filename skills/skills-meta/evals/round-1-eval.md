# skills-meta Round 1 Eval

Date: 2026-05-08

## Scope

Validate the `skills-meta` skill package against skill-creator guidance, then
exercise three realistic prompts against the bundled helper.

## Structural Validation

| Check | Result | Notes |
|-------|--------|-------|
| `quick_validate.py` | pass | `Skill is valid!` Runtime: `0.036s`. |
| YAML/frontmatter parse | pass | `SKILL.md` frontmatter keys are exactly `['name', 'description']`. Canonical version lives in `manifest.yaml`. |
| `agents/openai.yaml` parse | pass | `interface.display_name`, `interface.short_description`, `interface.default_prompt`, and `policy.allow_implicit_invocation` parsed cleanly. |
| manifest presence | pass | `manifest.yaml` contains an active `skills-meta` entry with `runtime: portable` and 14 active skills total. |
| `manifest.install_roots` parse | pass | `windows`, `wsl`, and `legacy` groups parsed; helper picks them up via `flatten_roots`. |

## Behavioral Benchmark

| Prompt | Expected behavior | Observed behavior | Result | Timing |
|--------|-------------------|-------------------|--------|--------|
| `inventory all skills` | List installed skills, show versions, flag drift, and summarize counts in a phone-friendly format. | Reported `skills scanned: 100`, `drifted: 57`, `duplicates: 43 (across 28 skills)`, and `unreadable roots: 3` (all `manifest no-skills-found`). The expanded root set covers Windows, WSL, and legacy installs; manifest-listed roots that are empty surface as unreadable instead of silently skipping. | pass | `0.191s` |
| `single-skill version check` | Focus on one skill and show installed version vs canonical version with drift notes. | Reported `skills-meta` as `vmissing`, canonical `v1.0.0`, runtime `portable`, status `drift`, issues `missing-version, missing-last-updated`. | pass | `0.194s` |
| `frontmatter-fix suggestion` | Print a copy-pasteable frontmatter block only, without rewriting files. | Returned a suggested frontmatter block for `skills-meta` with `name`, `version: 1.0.0`, `last-updated: 2026-05-08`, and `description`. Suggestion only; the actual skill frontmatter remains `name` + `description`. | pass | `0.181s` |
| `fix-duplicates dry run` | When the same skill name appears at multiple roots, print a keep/remove plan; never delete without `--apply`. | Listed 28 duplicate skill names with one `keep:` line and one or more `remove:` lines per group; chose the manifest-pinned copy when present (`gh-fix-ci` kept the repo copy over the `~/.codex/skills` copy). Footer reminded the user about `--apply`. | pass | `0.173s` |
| `simulated extra root via --root` | Honor an additional root and surface a missing root with origin `cli`. | Picked up `test-skill v0.1.0` from `/tmp/skills-meta-fixture/skills/test-skill` as `unknown` (not in manifest) and reported `cli missing /tmp/this-does-not-exist` in the unreadable section. | pass | `0.18s` |
| `simulated extra root via SKILLS_META_ROOTS` | Same input via env var; missing path tags as `env`. | Reported `env missing /tmp/also-missing` in the unreadable section. | pass | `0.18s` |
| `--mode inventory --json` | Emit machine-readable output covering records, unreadable roots, and duplicate groups. | Emitted valid JSON with `records: 100`, `unreadable: 3`, `duplicate_groups: 28`. The earlier `datetime.date` serialization bug in `manifest.last_updated` was fixed via `_json_safe`. | pass | `0.18s` |
| `--mode sync` dry run, two skills | Show a plan of what would copy/keep/skip into a target install root. | For `--target /home/tony/.codex/skills --skill merge-review,sprint-update` reported `! drift merge-review` (one cosmetic-newline difference) and `+ copy sprint-update` (missing on Codex). Plan footer reminded the user that `--force` is needed to overwrite drift. | pass | `0.20s` |
| `--mode sync --apply --force`, real install | Copy `sprint-update` into the Codex CLI install on Ubuntu and overwrite the drifted `merge-review` so the Codex sprint-manager agent sees the canonical Claude-side prompts. | Copied `sprint-update`, overwrote `merge-review`. Re-running the dry run reported `= keep` for both. `diff -q` confirmed byte-for-byte equality with the repo source. | pass | `0.21s` |

## Skill-Creator Compliance

| Guidance | Status | Notes |
|----------|--------|-------|
| Keep the skill lean | pass | Core logic lives in `scripts/skills-meta.py`; reference files hold schema, examples, and runtime roots. |
| Avoid extraneous docs | pass | No `README.md` or `CHANGELOG.md` was added under the skill. |
| Use bundled references for detail | pass | Detailed schema and output examples are split into references. |
| Validate agents metadata on update | pass | Added `agents/openai.yaml` with UI metadata and default prompt. |
| Follow current skill-creator frontmatter rules | pass | `SKILL.md` now uses only `name` and `description`; canonical version is tracked in `manifest.yaml`. |

## Remaining Risks

- The helper intentionally treats non-ISO or unparseable dates as drift, which is safe but may surface false positives for legacy skills.
- The inventory output reflects existing repo drift: all scanned skills currently lack version frontmatter, including `skills-meta` by design.
- `skills-meta` suggests frontmatter fixes but does not apply them, by design.
- `fix-duplicates --apply` performs `shutil.rmtree` on the directory containing the stale `SKILL.md`. It is gated by an interactive y/n per copy and refuses to run in non-TTY contexts, but a confused y at the prompt would still delete a directory. Treat it like any other interactive cleanup step — eyeball each path before confirming.
- Mobile installs still cannot be scanned directly; they show up only as `unreadable` roots when their paths exist in the manifest. The intended UX is "I see your phone install at this path is unreadable — please paste an export."
