#!/usr/bin/env bash
# Usage: issue-sweep.sh <owner/repo> <dry|exec>
# Closes open issues whose deliverable merged, detected by STRONG signal in a MERGED PR:
#   - PR title matches  (feat|fix|chore|docs|refactor|test|perf|build|ci)\(#N\)  or  ... #N:
#   - PR body matches    (Refs|Closes|Resolves|Fixes|Fix|Close|Resolve)\s*:?\s*#N
# Skips EPIC issues (title begins "Epic" OR has an "epic" label) — never auto-closes an epic.
set -euo pipefail
REPO="$1"; MODE="${2:-dry}"
PROTECT_EPICS="${PROTECT_EPICS:-}"   # comma-list of epic numbers to never close (active build)
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

# open issues (exclude PRs automatically; gh issue list is issues-only)
gh issue list --repo "$REPO" --state open --limit 1000 \
  --json number,title,labels,body > "$TMP/issues.json"
# merged PRs
gh pr list --repo "$REPO" --state merged --limit 1000 \
  --json number,title,body > "$TMP/prs.json"

# Build set of covered issue numbers -> first covering PR
python3 - "$TMP/issues.json" "$TMP/prs.json" "$REPO" "$MODE" "$PROTECT_EPICS" <<'PY'
import json, re, sys, subprocess, time
issues_f, prs_f, repo, mode, protect_s = sys.argv[1:6]
protect = set(int(x) for x in protect_s.split(',') if x.strip())
issues = json.load(open(issues_f))
prs    = json.load(open(prs_f))

# strong-signal extraction of issue numbers a PR claims to deliver
title_pat = re.compile(r'(?:feat|fix|chore|docs|refactor|test|perf|build|ci|style)\s*\(\s*#(\d+)\s*\)', re.I)
body_pat  = re.compile(r'(?:refs?|close[sd]?|resolve[sd]?|fix(?:e[sd])?)\s*:?\s*#(\d+)', re.I)

cover = {}  # issue_num -> pr_num (first/lowest)
for pr in prs:
    nums = set(int(n) for n in title_pat.findall(pr.get('title') or ''))
    nums |= set(int(n) for n in body_pat.findall(pr.get('body') or ''))
    for n in nums:
        if n not in cover or pr['number'] < cover[n]:
            cover[n] = pr['number']

def is_epic(it):
    t = (it.get('title') or '').strip().lower()
    if t.startswith('epic'): return True
    return any((l.get('name','').lower() == 'epic') for l in it.get('labels',[]))

to_close=[]; epics=[]; uncovered=[]
for it in issues:
    n = it['number']
    if is_epic(it):
        epics.append(it); continue
    if n in cover: to_close.append((n, it['title'], cover[n]))
    else:          uncovered.append((n, it['title']))

closing_story_nums = set(n for n,_,_ in to_close)
# epic is drained if, after closing the story set, no remaining-open issue references its number,
# AND the epic itself has a merged PR (its scaffold/handoff landed).
ref_pat_tmpl = r'#%d\b'
epics_to_close=[]; epics_keep=[]
# an epic stays open only if a remaining-open STORY (non-epic, no merged PR) still references it;
# inter-epic cross-references do NOT keep an epic open.
remaining_open_stories = [it for it in issues
                          if it['number'] not in closing_story_nums and not is_epic(it)]
for ep in epics:
    e = ep['number']
    rp = re.compile(ref_pat_tmpl % e)
    referenced = any(rp.search((it.get('body') or '')) for it in remaining_open_stories)
    if e in protect:
        epics_keep.append((e, ep['title'], 'PROTECTED-active-build'))
    elif (e in cover) and not referenced:
        epics_to_close.append((e, ep['title'], cover[e]))
    else:
        epics_keep.append((e, ep['title'], 'still-referenced' if referenced else 'no-merged-PR'))

print(f"\n===== {repo} =====")
print(f"open issues: {len(issues)} | merged PRs: {len(prs)}")
print(f"STORIES TO CLOSE (merged PR): {len(to_close)}")
for n,t,pr in to_close: print(f"  close #{n:<5} (PR #{pr})  {t[:66]}")
print(f"EPICS TO CLOSE (fully drained): {len(epics_to_close)}")
for n,t,pr in epics_to_close: print(f"  EPIC #{n:<5} (PR #{pr})  {t[:66]}")
print(f"EPICS KEPT OPEN: {len(epics_keep)}")
for n,t,why in epics_keep: print(f"  keep EPIC #{n:<5} [{why}]  {t[:60]}")
print(f"UNCOVERED stories (no merged PR — leave): {len(uncovered)}")
for n,t in uncovered: print(f"  keep #{n:<5}  {t[:66]}")

if mode == 'exec':
    closed=fail=0
    for n,t,pr in (to_close + epics_to_close):
        try:
            subprocess.run(['gh','issue','close',str(n),'--repo',repo],
                check=True, capture_output=True, text=True)
            closed+=1
            time.sleep(0.7)  # pace under ~500/hr secondary write cap
        except subprocess.CalledProcessError as e:
            fail+=1; print(f"  FAIL #{n}: {e.stderr.strip()[:140]}")
    print(f"  >>> {repo}: CLOSED {closed}, FAILED {fail}")
PY