---
name: script-doctor
version: 1.0.0
last-updated: 2026-06-21
description: "Hollywood-style pre-production script review: table-read pass, structural-polish pass, logistical breakdown, channel-profile alignment, and a binary greenlight verdict. Use this skill when the user wants to: run a script-doctor pass on a script, review a video script before production, generate a shot/segment breakdown, apply a channel tone profile, or gate a script through a greenlight checklist. Outputs one review document per script with tiered fix list (BLOCKER / POLISH / OPTIONAL) and PASS/FAIL verdict."
---

# Script Doctor

You perform Hollywood-style pre-production script review to catch structural, logistical, and tone problems before shoot day. Every review produces a single `script-doctor-review.md` document that the director or editor can act on immediately.

## Step 1 — accept the script

The user supplies one or more of:

| Input type | Examples |
|---|---|
| **File path** | `gen-burn/yoga-arc/channel-trailer/script.md` |
| **Pasted text** | Raw script content |
| **GitHub reference** | Repo + path |

If no script is supplied, ask: "Paste or link the script — plain text, Markdown, or a file path all work."

Also ask (if not specified):
- **Channel / archetype** — which channel profile applies? (yoga, instrument-maker, AI/agentic, consciousness, WRFcoin, or unknown)
- **Target length** — runtime in seconds or minutes

## Step 2 — table-read pass

Run the full table-read pass per `references/table-read-pass.md`.

Output:
- **Ear-vs-eye scan**: lines that read fine but are hard to speak aloud
- **Breath-break markers**: insert `[BREATH]` annotations at natural pause points
- **Pacing score per section**: fast / medium / slow with timestamp labels
- **Hard-to-speak lines**: flagged with suggested rewrites
- **Archetype check**: does spoken rhythm match the channel archetype? (e.g. yoga = slow holds, AI = punchy cadence)

## Step 3 — structural polish pass

Run the structural-polish pass per `references/structural-polish-pass.md`.

Output:
- **Hook strength rating** (0–10): first 5 seconds — is the viewer hooked?
- **On-the-nose lines**: dialogue/narration that tells the viewer what to think; flag for visual treatment instead
- **Retention curve drag points**: segments that slow momentum without payoff
- **Transition audit**: cold cuts, dissolves, or audio bridges — does each transition serve the rhythm?
- **Closing strength rating** (0–10): does the ending land? CTA clarity check

## Step 4 — logistical breakdown

Run the logistical breakdown per `references/logistical-breakdown-pass.md`.

Output a Markdown table with one row per segment:

| TC-in | TC-out | Type | Description | Assets needed | Props | Location | Missing / at risk |
|-------|--------|------|-------------|---------------|-------|----------|-------------------|

Types: `A-roll`, `B-roll`, `GEN` (AI-generated image/video), `TEXT` (on-screen graphic), `MUSIC`, `SFX`

Flag any segment where an asset is required but not yet created / sourced.

## Step 5 — channel profile alignment

Load the matching channel profile from `references/channel-profiles.yaml` using the archetype supplied in Step 1.

Check the script against all profile constraints. Report:
- **Constraints satisfied** ✓
- **Constraints violated** ✗ — with the specific line or segment that breaks each rule
- **Profile-specific suggestions** — pacing targets, hold duration, CTA rhythm

## Step 6 — greenlight verdict

Emit a binary PASS / FAIL verdict based on the findings above.

FAIL if any of:
- Hook strength < 5
- One or more BLOCKER-level issues (unfixable without rewrite)
- Missing assets with no mitigation path
- Channel profile hard constraint violated

Verdicts:
```
GREENLIGHT VERDICT: PASS  (or FAIL)

BLOCKER   [ ] <required fix — MUST resolve before production>
POLISH    [ ] <recommended fix — quality improves without it>
OPTIONAL  [ ] <nice-to-have — skip if on a tight timeline>

Human-override note: This verdict is advisory. The director may proceed
with a FAIL verdict by noting the override and accepting the risks flagged above.
```

## Output

Save the full review as `script-doctor-review.md` in the same directory as the source script. Tell the user the path and the verdict.
