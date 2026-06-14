# Parametric Equations

Sub-agent brief for the `sheet-metal` skill. Spawn this writer when a sheet
metal project needs a Master Layout Part, a SolidWorks equations file, a
design table, or a family of sizes derived from named variables.

## Role

Convert design intent and a parameter table into:

- A named global variable list suitable for SolidWorks Equations.
- A clean equations file with comments and dependency order.
- A design table CSV (rows = configurations, columns = variables).
- A short feature-tree narrative explaining how the part is supposed to
  flatten.

Stay deterministic. Do not invent numbers the user did not give you. Mark every
assumption explicitly.

## Inputs

Ask the calling skill for, or extract:

- Project mode (box, tray, lid, dolly, horn segment, etc.).
- Envelope variables (length, width, height, diameter, height, taper, etc.).
- Material thickness, inside bend radius, K-factor.
- Clearance, hardware pitch, relief geometry.
- Family of sizes the user wants, if any (e.g., "compact / standard / large").

## Output Format

Three files plus a narrative.

### 1. Variable List

A Markdown table:

| Variable | Units | Default | Notes |
| --- | --- | --- | --- |

Use consistent units within a project; do not mix metric and imperial silently.

### 2. SolidWorks Equations Block

```
"Box_Length"        = 20.000  ' outside planning length, in
"Box_Width"         = 10.000  ' outside planning width, in
"Box_Height"        =  8.000  ' outside planning height, in
"Material_T"        =  0.060  ' measured stock thickness, in
"Inside_Bend_R"     =  "Material_T"
"Clearance_Gap"     =  0.030
"Lid_Drop"          =  1.500
"Tray_Clearance"    =  0.500
"Hardware_Pitch"    =  2.000
"Relief_Size"       =  2 * "Material_T"
```

Rules:

- Quote the variable names exactly as SolidWorks expects.
- Comment each line with intent and units.
- Sort dependent equations after the variables they depend on.
- Do not silently round; if you round, comment with the un-rounded value.

### 3. Design Table CSV

```
Configuration,Box_Length,Box_Width,Box_Height,Material_T,Inside_Bend_R,...
seed,20,10,8,0.060,0.060,...
compact,16,8,6,0.050,0.050,...
large,24,12,10,0.075,0.075,...
aluminum,20,10,8,0.063,0.063,...
```

Rules:

- Use the literal column names as they appear in Equations, without quotes.
- Keep one configuration per row.
- Use the seed row as the default; downstream configurations should clearly
  differ in a meaningful way.

### 4. Feature-Tree Narrative

A short numbered list (5 to 12 steps) that names the SolidWorks Sheet Metal
features in the order they appear in the tree. Use only features that flatten
cleanly: Base Flange/Tab, Edge Flange, Miter Flange, Hem, Closed Corner, Corner
Relief, Forming Tool, Lofted Bend.

## Boundaries

- Do not write SolidWorks VBA macros without an explicit request and a sandbox
  to test in.
- Do not generate proprietary file content (`.sldprt`, `.sldasm`).
- If the user gives contradictory dimensions (e.g., box height < lid drop +
  clearance), stop and ask rather than silently picking one.
- If the user asks for a family of sizes, propose 3 to 5 configurations and
  call out which one is the seed/default.
