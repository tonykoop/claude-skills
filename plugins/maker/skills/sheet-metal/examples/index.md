# Examples

Real deliverables built with the `sheet-metal` skill. These are not templates
to copy blindly; they are concrete evidence of what a complete packet looks
like when this skill is doing its job.

## Stackable Sheet Metal Toolbox

**Location**: `C:\Users\Tony\Documents\GitHub\stackable-sheet-metal-toolbox`
(sibling repo to `claude-skills`).

**Brief that produced it**:

> Sheet Metal — produce all deliverables for a top-down SolidWorks assembly
> that can be parametrically driven for different sizes. The first size is
> similar to a toolbox at around 20 in wide x 8 in tall x 10 in deep. The
> design should be stackable like modular toolbox systems and include a dolly
> to move three or four around at a time.

**What the packet contains**:

- `README.md` with file index and authority statement
- `design-brief.md` with object, use case, seed envelope, assumptions, open
  measurements
- `parameters.csv` with named master variables (51 rows), each with source,
  confidence, and notes
- `solidworks-equations.txt` with copyable equations including derived stack
  envelopes (`Stack_Envelope_3_High = Box_Height * 3 + 3.000in`)
- `solidworks-design-table.csv` with four starter configurations: seed,
  compact, large, and aluminum alternate
- `solidworks-plan.md` with master layout part recipe, top-down part method,
  toolbox feature order, dolly feature order, configurations, mates, sheet
  metal defaults, and drawing-package targets
- `assembly-tree.csv`, `stacking-interface.md`, `dolly-plan.md`
- `bom.csv`, `hardware.csv`, `cut-list.csv`, `bend-table.csv`,
  `load-cases.csv`
- `flat-pattern-checklist.md`, `fabrication-plan.md`,
  `validation-checklist.md`
- `agent-record.md` recording source, references consulted, assumptions, and
  next human decisions

**Authority status**: Design and CAD planning authority only. Not fabrication
authority until actual hardware, stock, tooling, and reviewed SolidWorks flat
patterns are complete.

**What this example demonstrates**:

- A correct top-down SolidWorks master-layout pattern with planes, sketches,
  named dimensions, and derived production parts.
- A correctly-shaped parametric design table CSV that can be pasted into
  SolidWorks.
- Default artifact contract from `SKILL.md` realized as a complete packet.
- Authority discipline: every assumption has a confidence rating and a
  follow-up gate.
- Skill cross-routing: dolly load cases flag the safety-gate at the right
  threshold; vehicle/overhead/cat work would route to `maker-engineering`.

## How To Add A New Example

When this skill produces a packet you want to keep as canonical evidence,
either:

1. Build the packet into its own sibling repo (preferred for substantial
   projects), and add an entry here pointing at it.
2. Drop a curated subset under `examples/<project-name>/` if the packet is
   small and you want it to ship with the skill.

Each example entry should record: the brief that produced it, what files it
contains, the authority status, and what the example demonstrates about the
skill.
