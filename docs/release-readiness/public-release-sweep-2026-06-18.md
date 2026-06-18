# Public-Release Sweep - 2026-06-18

Issue: https://github.com/tonykoop/claude-skills/issues/10

Follow-up sweep on fresh `origin/main` after the June 15/16 release-readiness
reports. This is a blocker inventory, not a scrub commit: the repo remains
private-first until the items below are resolved or intentionally accepted.

## Commands

Run from the repo root.

```sh
rg -n -F -e "/home/tony" -e "/mnt/c/Users/Tony" -e "C:\\Users\\Tony" \
  README.md docs plugins codex scripts manifest.yaml --glob '!dist/**'

rg -n "(ghp_[A-Za-z0-9]{20,}|gho_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|BEGIN (RSA|OPENSSH|EC|DSA)? ?PRIVATE KEY|password\\s*[:=]\\s*['\"][^'\"]{6,}|xox[baprs]-[A-Za-z0-9-]+)" \
  README.md docs plugins codex scripts manifest.yaml --glob '!dist/**'

rg -n "[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}" \
  README.md docs plugins codex scripts manifest.yaml --glob '!dist/**'

rg -n -i "wrfcoin|n5" README.md docs plugins codex scripts manifest.yaml \
  --glob '!dist/**' --glob '!docs/benchmarks/**' \
  --glob '!plugins/maker/skills/sheet-metal/sheet-metal-workspace/**'

rg -n "Copyright \\(c\\)" LICENSE README.md docs plugins codex scripts manifest.yaml \
  --glob '!dist/**'
```

## Results

| Area | Result | Release status |
|---|---:|---|
| Obvious token/key/password/private-key patterns | 0 lines | pass for this pattern set |
| Private home paths | 109 lines across 47 files | blocker |
| Email addresses | 10 lines across 6 files | review/blocker for non-author addresses |
| WRFCoin/N5 references, excluding benchmark blobs | 42 files | provenance-label review |
| License/copyright owner strings | `LICENSE:3: Copyright (c) 2026 Wrfcoin` | owner decision needed |

## Blockers

### Private paths

The June 15 scan found ~88 private-path lines across 38 files. This run finds
109 lines across 47 files because newer plugin docs and eval fixtures added
more explicit local paths. `manifest.yaml` install roots can remain if they are
clearly documented as local examples; the rest should be generalized to
`<repo-root>`, `<workspace>`, `<skill-root>`, or environment variables.

Hotspots:

- Windows PowerShell scripts under `scripts/` still default to
  `C:\Users\Tony\Documents\GitHub\claude-skills`.
- `file-a-patent`, `sheet-music`, `instrument-maker`, `sheet-metal`,
  `idea-incubator`, `run-swarm`, `ci-triage`, `scaffold-hygiene`, and
  `sprint-supervisor` docs/evals still include Tony-local roots.
- Some paths are intentionally illustrative or refusal-test prompts, but they
  need labels so public readers do not treat them as required configuration.

### Email addresses

The hard-coded Wolfram account remains:

- `scripts/wolfram-cloud-sync/wolfram_sync.wls:82` (`wrfcoin@gmx.com`)

Author metadata such as `tonykoop@gmail.com` may be acceptable if Tony wants it
public, but non-author operational accounts should move behind env/config.

### License owner

`LICENSE` currently names `Wrfcoin` as copyright holder. That may be correct for
the original provenance, but the README now positions the repo as a broader
skill ecosystem. Before public release, decide whether the public owner should
stay `Wrfcoin`, become `Tony Koop`, or use another legal entity.

### WRFCoin/N5 provenance

WRFCoin is acceptable when explicitly labeled as historical provenance or a
project-specific skill lane. N5/local-host topology should not appear as a
default public operating assumption. Keep it in project-specific examples,
private adapters, or clearly labeled illustrative config blocks.

## New Gates To Keep

- Public-release scans should report both file counts and line counts, not only
  a sample list, so regressions are visible.
- Local-machine defaults in scripts must be configurable through parameters,
  environment variables, or documented placeholders before public release.
- License ownership needs an explicit release signoff, separate from secret and
  path scans.
- Very large generated benchmark artifacts should be excluded from broad
  provenance scans or summarized separately; otherwise real release blockers are
  buried in generated output.

## Next Reviewable Scrub Slices

1. Parameterize the PowerShell marketplace/sync scripts and Wolfram sync
   defaults.
2. Generalize private paths in public-facing `SKILL.md` files first, then
   references/evals.
3. Label WRFCoin/N5 examples as provenance or move them into project-specific
   docs/adapters.
4. Decide and update the license owner string.
