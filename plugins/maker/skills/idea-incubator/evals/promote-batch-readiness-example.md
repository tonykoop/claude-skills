# Promote-Batch Readiness Helper Example

Command:

```bash
python skills/idea-incubator/scripts/promote_batch_readiness.py \
  --issues-json skills/idea-incubator/evals/promote-batch-readiness-fixture.json \
  --anchor-root /mnt/c/Users/Tony/Documents/GitHub \
  --inventory-csv /mnt/c/Users/Tony/Documents/GitHub/archive-inventory-2026-05-09.csv
```

Expected shape:

```markdown
| Issue | State | Evidence | Blockers | Best next route | Decision |
|---|---|---|---|---|---|
| #55 Weather Balloon Camera Vessel - recover and scaffold repo | promote, capture | anchors: /mnt/c/Users/Tony/Documents/GitHub/_archive-recovery-staging/weather-balloon-camera-vessel; inventory: archive-inventory-2026-05-09.csv:147; https://github.com/tonykoop/claude-skills/issues/55 | confirm route, provenance, and close vs refs | maker-engineering / makerspace | promote |
| #53 Full inventory pass of D archive | ready-now, capture | inventory: archive-inventory-2026-05-09.csv:1; https://github.com/tonykoop/claude-skills/issues/53 | none identified | skills-meta or target skill | close / comment |
| #62 Verify sundials actually exist in archive | needs-clarification, capture | anchors: /mnt/c/Users/Tony/Documents/GitHub/sundials; https://github.com/tonykoop/claude-skills/issues/62 | missing key detail | idea-incubator review | comment / defer |
```

Line numbers may differ when the inventory source changes. For whole-inventory
issues, line 1 means "inventory file provided" rather than a matching artifact
row. The important behavior is that the helper flags existing anchors,
inventory-backed evidence, and clarification blockers before a human chooses
promote, close, or defer.
