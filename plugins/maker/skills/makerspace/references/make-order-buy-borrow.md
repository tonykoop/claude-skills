# Make / Order / Buy / Borrow

Use this reference when the user needs a decision about tooling,
fixtures, templates, or setup aids.

## Decision lens

Ask these in order:

1. Will this be reused enough to justify custom fabrication?
2. Is time-to-first-good-part more important than minimizing spend?
3. Does the job need a precision or rigidity level that only one option
   can provide?
4. Can the current shop build the aid safely with the tools on hand?
5. Will lead time or availability make a theoretically better option lose?

## Default heuristics

- **Make**
  Prefer when geometry is custom, batch size is meaningful, and the shop
  can build the aid quickly with known materials.
- **Order**
  Prefer when a semi-custom or precision component is needed and the lead
  time still fits the schedule.
- **Buy**
  Prefer when the item is commodity tooling and the commercial option is
  safer, faster, or more accurate than a scratch build.
- **Borrow**
  Prefer when the need is short-lived, the geometry is still evolving, or
  the shop already has a near-fit fixture that avoids waste.
- **Adapt existing**
  Prefer when a modular vise, fixture plate, template, or stop system can
  do the job with small modifications.

## What a recommendation should mention

- chosen path
- why it wins
- what would change the decision
- the biggest risk in the chosen path
- the best rejected alternative
