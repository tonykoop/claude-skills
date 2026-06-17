# Public-Content Scan — 2026-06-15

Issue: https://github.com/tonykoop/claude-skills/issues/10

Reproducible sweep of the repo for content that should not ship to a public
audience: secrets/tokens, private home paths, personal data, private
hostnames, and project-specific (WRFCoin / N5) coupling. Run from a clean
checkout of `main` at commit `f190f3e`.

Context: Tony is taking WRFCoin public (testnet imminent), so the **WRFCoin
project name itself is acceptable as labeled provenance**. The action items
below therefore target *private paths and personal data*, not the WRFCoin
name.

## Method (reproducible)

```sh
# secrets / tokens
grep -rInE "ghp_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|BEGIN (RSA|OPENSSH|EC) PRIVATE KEY|password\s*[:=]\s*['\"][^'\"]{6,}" --exclude-dir=.git .

# private home paths
grep -rInE "/home/tony|/mnt/c/Users/Tony|C:\\\\Users\\\\Tony" --exclude-dir=.git .

# wrfcoin references
grep -rIl -i "wrfcoin" --exclude-dir=.git .

# stray emails (author email tonykoop@gmail.com is intentional)
grep -rInoE "[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}" --exclude-dir=.git .
```

## Findings

### 1. Secrets / tokens — ✅ CLEAN

No API keys, OAuth tokens, AWS keys, private-key blocks, or inline passwords
matched. No action.

### 2. Private home paths — ⚠️ GENERALIZE (38 files)

`/home/tony/...`, `/mnt/c/Users/Tony/...`, and `C:\Users\Tony\...` appear on
~88 lines across 38 files. These are personal-machine paths and should be
generalized to placeholders (`<user-home>`, `<repo-root>`, `~/`), **except**
`manifest.yaml install_roots`, which legitimately documents real install
targets — keep those but consider a comment that they are example/local
roots.

Hotspots (lines):

| Lines | File | Treatment |
|---|---|---|
| 11 | `manifest.yaml` | Keep (real install_roots) — annotate as local examples |
| 6 | `plugins/coding/skills/scaffold-hygiene/SKILL.md` | Generalize → `<repo-root>` |
| 4 | `scripts/migrate-to-marketplace.ps1` | Generalize or move to a local-only script |
| 4 | `scripts/consolidate-to-two-plugins.ps1` | Generalize or move to local-only |
| 4 | `plugins/maker/skills/sheet-metal/references/benchmarks-and-versioning.md` | Generalize |
| 4 | `plugins/maker/skills/idea-incubator/evals/promote-batch-readiness-example.md` | Generalize (eval fixture) |
| 4 | `plugins/maker/skills/file-a-patent/SKILL.md` | Generalize |
| 3 | `scripts/verify-and-finish-marketplace.ps1`, `scripts/sync-installed-skills.ps1` | Generalize or local-only |
| 3 | `plugins/maker/skills/sheet-music/evals/handoffs/02-native-american-flute.md` | Generalize (eval fixture) |
| 2 | `sprint-supervisor` SKILL.md + `references/morning-summary.md` | Tracked under #164 staged extraction |
| 2 | `run-swarm/SKILL.md`, `ci-triage/SKILL.md` | Generalize or label `Example, illustrative:` |
| 1–2 ea | 20 further maker/coding eval + doc files | Bulk generalize pass |

Full line-level list is reproducible with the home-path grep above.

### 3. Stray email — ⚠️ REVIEW (1)

`scripts/wolfram-cloud-sync/wolfram_sync.wls:82` hard-codes `wrfcoin@gmx.com`.
The author email `tonykoop@gmail.com` (plugin.json `author`) is intentional;
this second address should be moved to an env var / config placeholder rather
than committed in a script.

### 4. WRFCoin references — ℹ️ PROVENANCE OK (40 files)

40 files reference WRFCoin (README, LICENSE, the entire `coding` plugin's
sprint/CI/swarm skills, docs, marketplace metadata). Per Tony's decision
(WRFCoin going public), these are acceptable **as labeled provenance**. Where
WRFCoin appears inside an otherwise-generic skill, prefer an `Example,
illustrative:` label (per the public-release checklist convention) so the
skill still reads as project-neutral.

### 5. "N5" references — ℹ️ REVIEW (14)

14 `N5` mentions (a private sprint-topology / node label) appear mostly in
the sprint skills. Lower-stakes than paths, but generalize where they leak
internal topology assumptions; otherwise label as provenance.

## Recommended order of operations

1. Move/parameterize the stray email in `wolfram_sync.wls` (finding 3).
2. Bulk-generalize private home paths outside `manifest.yaml` (finding 2).
3. Annotate `manifest.yaml install_roots` as local-example roots.
4. Apply `Example, illustrative:` labels to WRFCoin/N5 mentions inside
   generic skills (findings 4–5).
5. Re-run the four greps above; expect secrets clean and home-path hits only
   in `manifest.yaml` (annotated).

## Status

This is a findings report, not a scrub commit. Each treatment above is a
discrete follow-up so the scrub stays reviewable. Findings 2 + 3 are the only
hard blockers for going public; 4 + 5 are provenance-labeling polish.
