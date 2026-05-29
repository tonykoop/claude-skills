# Why 5052-H32 (Not 7075, Not 6061)

The user asked for "forgiving aluminum" specifically because middle schoolers will hit walls, get T-boned, and drop the bot off the workbench. Here is the reasoning, written so the team's parent/mentor can defend the choice.

## The Three Candidates

| Property | 5052-H32 | 6061-T6 | 7075-T6 |
|---|---|---|---|
| Yield strength | 193 MPa | 276 MPa | 503 MPa |
| Ultimate strength | 228 MPa | 310 MPa | 572 MPa |
| Elongation at break | 12% | 12% | 11% |
| Bend radius (thin sheet) | 1.0T inside | 1.5-2.0T inside | 4-6T inside (cracks!) |
| Weldability | Excellent | Good | Poor |
| Corrosion resistance | Excellent | Good | Fair |
| Impact behavior | DEFORMS plastically | Deforms then cracks | CRACKS or shatters |
| Cost (small qty) | Low | Low | High |
| Bend-it-back-in-a-vise repairability | Excellent | Marginal | NO (breaks) |

## The Verdict
**5052-H32** because:
1. It bends instead of breaks. A dented wedge can be hammered flat between matches; a cracked 7075 wedge is scrap.
2. The lower yield strength **is the feature, not the bug** in this application. The shell is designed to deform and absorb energy, like a car crumple zone. A rigid 7075 shell transmits shock straight into the motors and electronics.
3. 5052 bends at a tighter radius without cracking, so the wedge geometry is achievable in 1.6 mm sheet without specialized tooling.
4. Easy to source: any local metal supplier or SendCutSend stocks 5052 in 0.063".

## Where 6061 IS used
The internal frame plate (motor mount tray) uses **6061-T6 at 3 mm**. This part needs stiffness, not impact tolerance — it lives inside the crumple zone. 6061 is plenty for it, and the extra strength keeps motor mount holes from elongating.

## Where 7075 is the wrong call here
7075 is amazing for control-bot weapons, top plates on hardened brushless heavyweights, and machined arms. But:
- It work-hardens and **cracks on impact** in thin sheet form.
- Welding it ruins the temper.
- It corrodes more aggressively, which matters in a humid garage workshop.
- The price doesn't justify itself when the design assumes the armor will deform.

## Practical sourcing
- SendCutSend, OSH Cut, or Xometry will laser-cut 5052 at 0.063" and bend it to your spec — typical turnaround 5-7 days.
- Local supplier alternative: Metal Supermarkets carries 12"x12" sheets for around $15-25.
- Buy TWO blanks. The team will fold the first one wrong. This is not a pessimistic estimate.
