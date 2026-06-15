# Weekly load review template

Used by weekly load review mode. Lay candidate work against the teaching
schedule, protect recovery, and place at most one heavy item per protected day.
Output is a week grid, not a backlog dump.

## Inputs to gather

- Teaching blocks for the week (stated, or read from Google Calendar).
- Hard deadlines.
- Candidate tasks with rough effort/energy (or `idea-incubator` labels).
- Any days the user has already flagged as off / travel / family.

## Rules

- After a heated or back-to-back teaching block, the **next** slot is
  recovery-protected: no `energy:high` task placed there.
- At most **one** `slot:deep` or `slot:weekend` item per day.
- Leave at least one fully open rest window in the week. If the week has no
  room for rest, flag it as overcommitted and recommend cuts — do not just
  pack it.
- Deadlines may override a recovery window only with an explicit user OK; note
  it as a borrow against recovery.

## Grid template

```
Week of: ____

Mon  | teaching: ____ | recovery? __ | planned: ____________________
Tue  | teaching: ____ | recovery? __ | planned: ____________________
Wed  | teaching: ____ | recovery? __ | planned: ____________________
Thu  | teaching: ____ | recovery? __ | planned: ____________________
Fri  | teaching: ____ | recovery? __ | planned: ____________________
Sat  | teaching: ____ | recovery? __ | planned: ____________________
Sun  | teaching: ____ | recovery? __ | planned: ____________________

Heavy items placed (max 1/day): ____
Protected rest window(s): ____
Deadlines this week: ____
Overcommit flag: yes / no  (if yes, suggested cut: ____)
```

## Output discipline

Return the filled grid plus a 1–2 line summary ("two deep slots, Thu protected
after the heated class, one rest window Sun"). No reflection, no scoring.
