# Changelog — scaffold-hygiene

## 0.2.0 — 2026-06-19

- Add first machine-runnable eval suite (`evals/evals.json`): 4 evals covering
  four-agent parallel launch, launch-blocker early stop, dedup before filing
  issues, and trigger-threshold check.
- Add manifest.yaml entry (skill was missing from canonical manifest).

## 0.1.0 — 2026-05-20

- Initial release. Read-only scaffolding hygiene sweep across WRFCoin multi-repo
  workspace: 4 parallel sub-agents covering workspace/build/CI, env vars/Docker,
  cross-repo API contracts, and docs/operator guides. Files GitHub issues for
  real drift; writes timestamped report.
