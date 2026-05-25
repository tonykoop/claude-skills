# Promote-Batch Readiness Helper

Use this helper when a capture cluster needs a decision matrix before
promotion, especially when live GitHub access may be flaky.

## Offline-first workflow

1. Save issue evidence when GitHub works:

   ```bash
   gh search issues label:capture repo:OWNER/REPO --limit 100 \
     --json repository,number,title,state,labels,createdAt,updatedAt,url \
     > /tmp/capture-issues.json
   ```

2. Run the helper with any local anchor roots and archive inventories:

   ```bash
   python skills/idea-incubator/scripts/promote_batch_readiness.py \
     --issues-json /tmp/capture-issues.json \
     --anchor-root /path/to/workspace \
     --inventory-csv /path/to/archive-inventory.csv
   ```

3. Use the output as the first draft of the Promote-batch readiness matrix.
   Review every `promote`, `close / comment`, and `comment / existing anchor`
   decision before taking action.

## Existing-anchor checklist

Before recommending a new repo or new downstream issue, check:

- Does a local repo, staging folder, or upstream system already hold the
  deliverable?
- Does an inventory CSV prove the source artifact already exists?
- Is the capture actually a request to reconcile an existing anchor rather
  than create a new target?
- If the deliverable is already satisfied, should the source issue get a
  comment and close instead of promotion?
- For recovery/import work, should the source issue stay open with `Refs #N`
  until an evidence ledger lands?

## GitHub fallback notes

`gh search` output fields can vary by command form, and connectivity can be
uneven. Prefer resilient collection:

- If `mergedAt` is unavailable, request `closedAt` and infer merged state from
  PR state or a later `gh pr view`.
- If a broad search fails, retry with `gh issue list --repo OWNER/REPO` or
  `gh pr list --repo OWNER/REPO`.
- If the API is unavailable, use saved JSON plus local sprint docs and mark the
  recommendation as fallback evidence.
- Record failed commands and retries in validation notes so future reviewers
  can distinguish stale local evidence from live API evidence.
