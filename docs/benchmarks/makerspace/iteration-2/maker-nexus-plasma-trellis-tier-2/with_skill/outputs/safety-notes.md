# Safety Notes — Plasma Cutting + Powder-Coat Prep

## Plasma-specific risks

- **Arc UV/IR.** Plasma arc emits intense UV. Required: ANSI Z87
  shaded glasses #5 minimum (#6 better at 45 A). Auto-darkening
  welding helmets work but are overkill. **Don't look at the arc
  directly even briefly** — UV exposure is cumulative.
- **Fume.** Cutting mild steel produces iron oxide and manganese
  fume. Maker Nexus's plasma table is downdraft; confirm the
  downdraft fan is running before starting any cut. If the fan is
  offline, do not cut. A P100 respirator is a backup, not a
  substitute, for table ventilation.
- **Slag and sparks.** Plasma sprays sparks 6-10 ft. Clear the
  zone of any combustibles (rags, sawdust drift from woodshop,
  cardboard). Cotton or wool clothing only — synthetics melt and
  stick to skin.
- **Electric shock.** The plasma torch carries pilot-arc voltage
  even between cuts. Never touch the torch tip with bare hands.
  Power off and unplug before changing consumables.
- **Hot metal.** Cut edges are 400-600 deg F immediately after the
  cut. Welding gloves or kiln gloves only — leather work gloves
  will char through.
- **Compressed air.** The torch needs 90+ psi clean dry air. A
  burst air hose is a whip hazard; check fittings before
  pressurizing.

## Material risks (mild steel only)

- This packet is mild steel A36, hot-rolled, pickled & oiled.
  **Do not** substitute galvanized steel — zinc fume from
  galvanized causes "metal fume fever" and the plasma will
  vaporize the coating. **Do not** substitute stainless without
  re-checking ventilation; chromium fume from stainless is a
  separate hazard.
- The "pickled and oiled" finish has a thin rust-preventive oil.
  Wipe down before cutting; oil flare-up is brief but startling.

## Powder-coat handoff risks

- **Bare-metal handling.** Body oil from skin contaminates
  powder-coat adhesion. Wear nitrile gloves after the final
  acetone wipe.
- **Acetone.** Flammable, ventilate. Don't wipe down near the
  plasma table.
- **Sandblast prep at the coater** is their problem, not yours,
  but specify: "abrasive blast to SSPC-SP6 commercial blast
  before powder application." This level of prep is standard for
  outdoor steel.

## Lifting and ergonomics

- The finished part is ~30 lb but 86 in long. Two-person lift.
  Don't try to walk it solo through the shop — the moment of
  inertia at 86 in is enough to torque a wrist if it tips.
- Edges are sharp post-deburr. Heavy gloves for handling.

## Cert check (Maker Nexus seed profile)

- (cleared) `shop-safety-cert` — prerequisite for any metalshop work.
- (cleared) `metalshop-cert` — covers metalshop-area, which on the
  seed profile covers plasma. Tony confirmed cleared.

## What to do if something goes wrong

- **Torch arc won't initiate / sputters.** Stop. Replace
  electrode + nozzle as a set. The most common cause is wet air;
  drain the air filter and try again.
- **Fire on the table.** CO2 extinguisher (not water) on the
  table itself; water on combustibles around the table. Plasma
  table slats themselves are non-combustible.
- **Cut goes off-path mid-program.** Hit cycle-stop, not e-stop
  unless the situation is dangerous. Investigate before
  restarting — usually a part that shifted.
- **You feel a tingle from the torch.** Stop, power off, find
  staff. Electrical fault.
