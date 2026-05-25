# Service Access Plan — "60 Second Tournament Turnaround"

A bracket-style tournament gives ~5 minutes between matches. The nieces need to swap a battery, check fasteners, and possibly hammer out a dent in that window. Here is the access plan.

## Service Time Targets
| Operation | Time | Tools |
|---|---|---|
| Battery swap | 15 sec | None (velcro strap) |
| Top deck removal | 45 sec | 2.5 mm hex key |
| Wheel replacement | 3 min | 2.5 mm hex + 1.5 mm hex |
| Motor swap (one side) | 8 min | 2.5 mm hex + 5 mm wrench |
| Wedge tip straightening | 2 min | Hammer + soft block |
| Full disarm to safe state | 5 sec | Pull arming link |

## Access Layout (top view)

```
   FRONT (wedge)
   +---------------+
   |   . . . . .   |   . = M3 top deck bolts (6x perimeter)
   |  +---------+  |
   |  |  BATT   |  |   removable cover plate over battery
   |  |  COVER  |  |   (2x M3 bolts, captive in cover)
   |  +---------+  |
   |     [ARM]     |   arming link bolt (M4 hex, accessible without opening shell)
   |   . . . . .   |
   +---------------+
   REAR
```

## The Arming Link (Kid-Safe Power Switch)
- A removable bolt-and-lug that physically completes the battery-to-ESC circuit
- M4 button-head bolt through a brass lug on each end of a 30 mm long copper strip
- When bolt is OUT: bot is unpowered. Period. No software, no electrons.
- When bolt is IN: bot is armed.
- Designed so the bolt's hex socket sits flush with the top deck.
- Drivers MUST insert the link only after placing the bot in the arena, and MUST remove it before picking the bot up. This is standard combat robotics practice and tournament safety officials will check.

## Battery Mount Strategy
- Battery sits in a foam-lined pocket molded into the inside of the top deck
- Velcro strap (industrial hook-and-loop) runs across the battery
- No screws touch the battery — never compress a LiPo with a fastener
- Pocket is 6 mm deeper than battery thickness so a damaged (puffy) LiPo can still be removed without prying

## Top Deck Service Workflow (45-second target)
1. Pull arming link (5 sec)
2. Verify status LED is OFF (1 sec)
3. Unscrew 6x M3 top deck bolts with 2.5 mm hex key (20 sec — keep bolts in magnetic tray)
4. Lift top deck straight up — wiring loom is long enough to lay it beside the bot (5 sec)
5. Access electronics (battery, ESC, receiver) (remaining time)

## Wedge Tip Dent Repair (2-minute field repair)
1. Pull arming link.
2. Place bot upside-down on a clean rag.
3. Lay a hardwood block against the inside of the wedge face.
4. Tap the OUTSIDE of the dent with a soft-faced mallet or rubber hammer.
5. Reseat the front edge against the arena floor for ground gap check.

This is the entire reason the chassis is 5052-H32. A 7075 wedge would be scrap; this one is back in the arena.

## Spares Kit for the Pit Table
| Item | Qty | Note |
|---|---|---|
| Charged 3S 450 mAh LiPos | 4 | Two in rotation, two reserves |
| Spare wheel (assembled w/ hub) | 2 | One per side |
| Spare drive motor | 1 | Pre-wired with bullet connectors |
| Spare arming link | 1 | They get dropped |
| M3 button head x 8mm | 20 | They get lost |
| 2.5 mm hex key | 2 | One always wanders off |
| Soft-faced mallet | 1 | For wedge repair |
| Hardwood block | 1 | Backing for hammer work |
| Roll of gaffer tape | 1 | Universal field repair |
| Zip ties (assorted) | 10 | Cable management + emergency |
| Sharpie | 1 | Tag spares, mark settle-in spots |
| Multimeter | 1 | Continuity check on arming link |
| LiPo charger + balance board | 1 | Charge between matches |
| Fire-safe LiPo bag | 1 | REQUIRED by most events |
