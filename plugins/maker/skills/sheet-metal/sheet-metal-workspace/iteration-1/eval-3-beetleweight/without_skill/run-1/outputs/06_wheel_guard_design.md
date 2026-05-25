# Wheel Guard Design

## The Problem
Beetleweight horizontal spinners (most common weapon class at middle-school events) target wheels. An exposed sidewall is a one-hit-kill. The nieces' bot needs wheels that survive a glancing blow.

## The Geometry
Each wheel guard is a **folded U-channel** that drapes over the top and outboard side of the wheel, with 180 degrees of coverage:
- Top of wheel: covered (drops weapon hits onto top of shell, not into tire)
- Outboard side of wheel: covered (deflects side hits)
- Inboard side: open (allows wheel/motor connection)
- Bottom: open (wheel needs to touch ground!)
- Front and rear of wheel: open by ~10 mm at the bottom (lets wheel reach floor without rubbing)

## Dimensions
- Material: 1.6 mm 5052-H32 (same stock as main shell — efficient!)
- Inside diameter: 44 mm (4 mm clearance over 40 mm OD wheel)
- Channel width: 28 mm (3 mm clearance over 25 mm wide wheel)
- Length: matches wheel diameter + 10 mm overhang front and rear
- Mount: two M3 bolts through the side wall of main shell into M3 locknuts behind the guard

## Why It Works
1. Horizontal spinner hits the outer guard, not the tire — guard dents, tire keeps spinning.
2. Vertical spinner hits the top guard — energy transfers into the chassis crumple zone rather than tearing the wheel off its shaft.
3. If a guard does deform onto the tire, the kids can bend it back with their hands in the pit between matches. **This is the killer feature for a novice team.**

## Trade-off: Weight
Two guards add about 44 g (3.4% of weight limit). This is the single best 44 g you can spend on a beetleweight wedge.

## Trade-off: Wheelbase Width
Guards push the overall bot width by 2 x 1.6 mm = 3.2 mm per side. Already accounted for in the 160 mm overall width spec.

## Alternative Considered: Skirts vs Guards
A common alternative is full-perimeter "skirts" that almost touch the floor. We rejected this for the niece team because:
- Skirts catch on arena floor seams and lift the bot.
- They demand precise build tolerances middle schoolers haven't developed yet.
- They don't actually protect wheels from spinner hits, only from being scooped.

Guards are simpler, more forgiving, and address the real threat (spinner damage to tires).
