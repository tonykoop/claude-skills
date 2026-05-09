# Tools — generic home shop

This is the fallback profile when the user hasn't named a specific
makerspace. The skill assumes a modest home shop with hand tools and
a few common power tools.

## When the skill loads this profile

- The user hasn't named a makerspace.
- The user explicitly says "home shop" or "garage" or similar.
- The user names a makerspace that doesn't have a profile yet — and
  hasn't provided a tool list.

## Override behavior

When the user adds detail to their setup ("I also have a lathe and a
drill press"), treat the user's stated tools as authoritative.
Ask whether to save those additions to a real profile under their
own slug for future use.

## Default tool kit

The default profile assumes:

- Hand saws (rip, crosscut, coping)
- Combination square, tape measure, marking gauge, marking knife
- Chisels and mallet
- Block plane
- Cordless drill with twist + spade + countersink bits
- Quick-grip clamps and a few F-clamps
- Random-orbit sander
- Handheld circular saw
- Handheld jigsaw
- Handheld router
- Sandpaper, glue, basic finishing supplies
- Bench or workbench surface

What the default profile does *not* assume:

- Tablesaw, bandsaw, jointer, planer, drill press
- CNC, laser, 3D printer
- Welder, mill, lathe
- Sewing machine

If the user has any of those, they should say so or pick a different
profile / make their own.

## When the project exceeds the home-shop kit

The shop-planner specialist will identify ops the user can't
realistically do with the default tools and either:
- Suggest a workaround using hand tools (slower but feasible),
- Suggest finding a makerspace or shop-mate for the operation, or
- Propose a redesign that avoids the operation.
