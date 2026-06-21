# Greenlight Gate Reference

The greenlight gate is the final step of every script-doctor run. It emits a binary PASS/FAIL verdict with a prioritized fix list.

## Verdict logic

**FAIL** if any of the following are true:

| Condition | Severity |
|---|---|
| Hook strength < 5 | BLOCKER |
| One or more BLOCKER-level issues from any pass | BLOCKER |
| Missing asset with no mitigation path | BLOCKER |
| Channel profile hard constraint violated | BLOCKER |
| Closing strength < 4 | POLISH (not a FAIL trigger; flag as POLISH) |
| More than 3 POLISH-level issues | POLISH (still PASS; list all) |

**PASS** if no BLOCKER conditions are triggered.

## Fix list tiers

| Tier | Meaning | Must fix before shoot? |
|---|---|---|
| `BLOCKER` | Will cause the video to underperform or be misleading | Yes |
| `POLISH` | Quality improves materially without it | Recommended |
| `OPTIONAL` | Nice-to-have; skip if on a tight timeline | No |

## Output format

```
══════════════════════════════════════════
GREENLIGHT VERDICT: PASS  (or: FAIL)
══════════════════════════════════════════

BLOCKER   [ ] <required fix — MUST resolve before production>
BLOCKER   [ ] <required fix — MUST resolve before production>

POLISH    [ ] <recommended fix — quality improves without it>

OPTIONAL  [ ] <nice-to-have — skip if on a tight timeline>

──────────────────────────────────────────
Human-override note: This verdict is advisory. The director may proceed
with a FAIL verdict by noting the override and accepting the risks flagged
above. Override should be documented in the production log.
══════════════════════════════════════════
```

## Phone-friendly summary

After the full verdict block, emit a one-line summary the director can read on a phone:

```
READY: [YES/NO] — [one-sentence reason or primary blocker]
```

## Integration with StudioPipeline

The greenlight gate output is consumed by the StudioPipeline pre-production review epic. When the READY line is `YES`, the script advances to the shoot schedule. When `NO`, it returns to the writer with the BLOCKER list only (POLISH and OPTIONAL are suppressed in the return message to reduce noise).
