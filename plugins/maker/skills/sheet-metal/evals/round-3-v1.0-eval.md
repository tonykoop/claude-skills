# Sheet Metal v1.0 Eval

Date: 2026-05-19
Skill path: `skills/sheet-metal`
Version: `1.0.0`

## Scope

First quantitative benchmark of the sheet-metal skill against a baseline (same
prompt, no skill). Three evals from `evals.json` selected for breadth:

- `eval-1-toolbox`: the actual stackable-toolbox brief that produced the
  example packet at `stackable-sheet-metal-toolbox/`.
- `eval-3-beetleweight`: combat-robotics + scripts + niece-friendly material.
- `eval-5-vehicle-rack`: vehicle/safety-gate behavior and authority discipline.

Workspace: `claude-skills/skills/sheet-metal-workspace/iteration-1/`.

## Setup

For each eval, two subagents ran in parallel:

- `with_skill`: instructed to read `SKILL.md` and relevant references before
  attempting the task, then save outputs into a designated folder.
- `without_skill`: same task prompt, no skill reference. Save to a parallel
  folder.

Each run's outputs were graded by `iteration-1/grade.py`, which checks each
assertion (from `eval_metadata.json`) against the concatenated content of the
output folder. Assertions were objective (file present, specific term used,
specific safety routing language present, etc.).

## Results

| Eval | With Skill | Baseline | Delta |
| --- | ---: | ---: | ---: |
| 1: stackable-toolbox-packet | 10 / 10 (100%) | 6 / 10 (60%) | +40 pp |
| 3: beetleweight-wedge-chassis | 8 / 8 (100%) | 5 / 8 (62%) | +38 pp |
| 5: rav4-flat-roof-rack-safety-gate | 6 / 6 (100%) | 2 / 6 (33%) | +67 pp |
| **Average pass rate** | **100%** | **52%** | **+48 pp** |

## Time / Tokens

| Config | Time | Tokens |
| --- | ---: | ---: |
| With Skill | 410.9 s avg | 73,694 avg |
| Baseline | 269.0 s avg | 46,720 avg |
| Delta | +141.9 s | +26,974 |

The skill is slower and heavier per-prompt because it loads references and
follows the workflow contract. The pass-rate lift more than justifies the
cost; the absolute time is still well under what a human would spend.

## What The Skill Caught That The Baseline Missed

Baseline runs were technically competent — clean documents, reasonable
material choices, sensible architecture. They failed on the things the skill
exists to enforce:

1. **Authority discipline**: baseline RAV4 output did not contain a
   "not road-ready" / "not certified for highway use" disclaimer. With-skill
   output stated this multiple times across multiple files.
2. **Safety routing**: baseline did not route to `maker-engineering` or a
   qualified review. With-skill output did, in both `design-brief` and
   `agent-record`.
3. **Specific script usage**: baseline beetleweight did not call
   `scripts/sheet_metal_math.py combat-budget` for the weight target. With-skill
   output ran the script and used its output.
4. **Default-artifact contract**: baseline files used inconsistent names
   (numbered prefixes, project-specific layouts). With-skill output matched
   the named-artifact contract (`design-brief.md`, `parameters.csv`,
   `solidworks-plan.md`, `bend-table.csv`, etc.), which makes downstream
   tooling (like `scripts/validate_packet.py`) work without per-project glue.
5. **Stacking interface language**: baseline used "interlock", "frustum",
   "pyramidal" — all valid words for the geometry, but the skill's
   `stacking-interface` vocabulary (clocking rim, perimeter rim, corner cleat,
   stack foot) makes the packet readable to anyone else using the skill.

## What The Baseline Got Right That The Skill Should Watch For

- The without-skill RAV4 baseline correctly identified Toyota's published
  176 lb dynamic roof load limit and pointed at Yakima as a certified-
  hardware foundation. The with-skill output kept the user load rating as an
  "open measurement" rather than going to find this kind of public OEM data.
  Worth thinking about: should the skill encourage looking up published OEM
  load ratings before treating them as "user must measure"?
- The without-skill beetleweight baseline produced a clear pit-kit and
  match-day checklist that the with-skill version didn't emphasize. The
  skill could note "tournament workflow" as a relevant supporting deliverable
  for combat-bot work.

## Residual Risks

- The eval set is small (3 prompts × 2 variants). The other 4 prompts in
  `evals.json` (horn, electronics, art, sconce) are not exercised here.
- Grading is keyword/structure-based, not semantic. A skilled baseline that
  used different vocabulary would underperform on grading even if the actual
  output was equivalent.
- Subagents read the skill from absolute paths and may behave differently
  under a real install (where the skill is in the `available_skills` list).
- Time/token delta is large enough that for very-low-stakes prompts the skill
  may feel heavy; that is the expected tradeoff for the safety discipline.

## Commands

```bash
# Re-grade after grader changes:
python3 sheet-metal-workspace/iteration-1/grade.py

# Re-aggregate after grader changes:
python3 -m scripts.aggregate_benchmark \
  sheet-metal-workspace/iteration-1 --skill-name sheet-metal

# Re-generate viewer:
python3 eval-viewer/generate_review.py \
  sheet-metal-workspace/iteration-1 \
  --skill-name "sheet-metal" \
  --benchmark sheet-metal-workspace/iteration-1/benchmark.json \
  --static sheet-metal-workspace/iteration-1/review.html
```

## Next Iteration Candidates

- Run the remaining 4 evals (horn, electronics, art, sconce) for breadth.
- Add a "research public OEM specs before treating them as user-measured" note
  to the vehicle module.
- Add a "tournament/match-day checklist" optional deliverable to the combat-
  robotics module.
- Consider tightening the SKILL.md description to reduce slow first-pass token
  cost while keeping triggering coverage.
