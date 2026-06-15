# Task-to-energy matching rubric

The core job: given a candidate task set and a capacity (`slot:*` + `energy:*`),
return a short ranked shortlist that fits the window.

## Output shape

```
[fits | stretch | skip today]  <task>  — one-clause reason
```

- `fits` — effort tier ≤ slot AND energy demand ≤ current energy.
- `stretch` — slightly over on one axis, or due-soon; name the cost.
- `skip today` — over budget on both axes, or cold-start in a low-energy slot.

Cap the list: 3 lines for `slot:micro`/`slot:focused`, 5 for
`slot:deep`/`slot:weekend`. Do not pad.

## Ranking rules (apply in order)

1. **Deadline first.** Anything due within the planning horizon surfaces near
   the top as `fits` or `stretch`, with the deadline stated. Deadlines beat
   energy fit.
2. **Energy honesty.** In `energy:low`, never rank a cold-start design or
   open-ended creative task first. Favor `ready-now`, mechanical, or closeout
   work. In `energy:high` + `slot:deep`/`slot:weekend`, favor the hardest
   blocked or highest-leverage item.
3. **Slot honesty.** Do not promise a multi-session build inside `slot:micro`.
   Offer its smallest real sub-step instead.
4. **Domain balance (weekly mode only).** Spread across `maker` / `instrument`
   / `yoga` / `skills` rather than stacking one domain on one day.

## Tie-breakers

- Prefer the task that *unblocks* others.
- Prefer the task that closes an almost-done item (momentum) over starting new.
- If two tasks tie, present both and let the user pick — do not invent a score
  to break the tie.

## When nothing fits

Say so in one line, then give the single smallest honest next action and an
explicit "or rest this slot" option. Example:

> Nothing here fits a low-energy 20 min. Smallest real step: file the
> bridge-photo measurement into the reverse-engineer note (5 min, mechanical).
> Otherwise this is a good slot to rest.

## Worked examples

### A. `slot:micro` + `energy:low`, mixed list

Candidates: "draft khaen acoustic test rig" (deep, high), "reply to Maker
Nexus checkout email" (trivial), "finalize chickadee cut-list CSV" (single,
ready-now).

```
fits        finalize chickadee cut-list CSV — ready-now, closeout, fits 30 min low
fits        reply to Maker Nexus checkout email — trivial, mechanical
skip today  draft khaen acoustic test rig — cold-start design, needs a deep+high slot
```

### B. `slot:weekend` + `energy:high`, deadline present

Candidates: "Tillandsia-on-bark prototype mount" (multi-step, due next class),
"organize photo archive" (deep), "sand bird-bath bowl" (single).

```
fits     Tillandsia-on-bark prototype mount — due next class; weekend+high is the right slot
fits     sand bird-bath bowl — single-session, good high-energy hand work
stretch  organize photo archive — deep but no deadline; only if energy holds after the mount
```

### C. nothing fits

`slot:micro` + `energy:low`, only deep tasks on the list → emit the
"nothing fits" line above.
