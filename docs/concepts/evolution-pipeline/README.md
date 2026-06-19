# Evolution Pipeline — prototype → finished-good (PLM/DFM, on-demand sourcing)

A scoping / form-factor decision sketch for [claude-skills#206](https://github.com/tonykoop/claude-skills/issues/206).
Status: **capture.** The issue's `Next step` is explicitly a decision —
*"Decide form factor: makerspace-skill extension vs. a StudioPipeline/evolution
repo. Then scope the Beta Vendor Broker (which on-demand API first)."* This doc
makes that decision and scopes the first engine. No code yet.

## What it is

A second StudioPipeline plugin — the **Evolution Pipeline** — that automates the
lifecycle of the *atoms* (PLM/DFM), running parallel to the studio-pipeline video
plugin. Three engines:

1. **Alpha Workspace Compiler** (pairs with `makerspace`) — downgrade master CAD
   fidelity to the user's local tool matrix: reslice to a printable shell,
   flatten a housing into laser-nested panels.
2. **Beta Vendor Broker** — hit on-demand-shop instant-quote + DFM APIs
   (Xometry / Protolabs / Hubs), emit an auto trade-off report
   (material / tolerance / lead-time / cost) instead of manual browser quoting.
3. **Production Master + BOM/PLM** — multi-level BOM, ECOs, flat patterns, GD&T
   drawing PDFs; sync to an open PLM (Duro / Aletiq).

## Decision 1 — form factor

**Recommendation: start as a `makerspace` skill extension, graduate to a
standalone `StudioPipeline/evolution` plugin at the Production engine.**

Rationale:

| Factor | makerspace extension | standalone plugin |
|---|---|---|
| Reuses existing make/order/buy/borrow + RFQ + lead-time budgets | ✅ already there (`references/make-order-buy-borrow.md`) | ❌ re-implement |
| Time to first value (Alpha + Beta) | fast — Alpha *is* makerspace's tool-matrix downgrade | slow |
| Production PLM scope (BOM/ECO/PLM sync) | strains a shop-floor skill | natural fit |
| Coupling to StudioPipeline video plugin | indirect | direct |

The Alpha engine is essentially makerspace's tool-matrix work already; the Beta
broker is a thin sourcing layer over the existing RFQ flow. Only the Production
engine (multi-level BOM, ECOs, PLM sync) outgrows a shop-floor skill. So: build
Alpha + Beta **inside makerspace** (lowest cost, immediate value), and spin out
`StudioPipeline/evolution` when the Production/PLM engine arrives.

## Decision 2 — Beta Vendor Broker: which on-demand API first

**Recommendation: integrate one provider behind a provider-agnostic
`QuoteRequest`/`QuoteResult` contract first; make Hubs/Xometry the reference
implementation, mock the rest.**

The risk is coupling the broker to one vendor's payload. So the first slice is
the **contract**, not the vendor:

```yaml
# QuoteRequest (provider-agnostic)
part_ref: housing-v3.step
process: cnc-milling          # maps to a Manufacturing Capability Index process (#205)
material: 6061-aluminium
tolerance_mm: 0.1
quantity: 10
finish: as-machined
```

```yaml
# QuoteResult (normalized across providers)
provider: hubs
unit_cost_usd: 42.10
lead_time_days: 9
dfm_flags: ["thin-wall@boss-3", "deep-pocket-aspect@4.2"]
material_substitution_hint: null
```

The auto trade-off report is then a sort/filter over a list of `QuoteResult`s.
Pick the first live provider by whichever has the most documented instant-quote +
DFM API; mock the others against the same contract so the broker is testable
offline (matching the offline-first posture of the idea-incubator scripts).

## makerspace skill gaps to close (relative to v1.2.0)

makerspace already has make/order/buy/borrow + supplier RFQ + lead-time budgets.
The Evolution Pipeline adds:

- **alpha→beta→production stage-gating** — a lifecycle state machine with an
  explicit gate between stages (Alpha shell verified → Beta quotes obtained →
  Production master released). Gate transitions should reuse the verification
  discipline from the governance/verification gates.
- **on-demand-shop API integration** — the Beta Vendor Broker above.
- **design-change register / variant iteration tracking** — an ECO-lite log so a
  variant's lineage and the *reason* for each change are traceable.

## How it composes

- **Inputs:** a master CAD + the [Manufacturing Capability Index (#205)](../manufacturing-capability-index/README.md)
  (process limits gate the Alpha downgrade and the Beta `process` field).
- **Outputs feed:** MakerBench's Physical Verification Track (#112), the quote
  bridge (#82), CostingAdapter (#81); and the StudioPipeline video plugin turns
  Evolution's material logs / inspection reports / DFM history into episode
  segments.

## Open questions

- Which on-demand provider actually exposes a usable instant-quote + DFM API
  today (vs. requiring a sales contact)? That decides the reference impl.
- Does the design-change register need to interoperate with an open PLM (Duro /
  Aletiq) from day one, or is a local ECO-lite log enough until Production?

## Scope

Decision + scoping RFC, no code. Resolves the #206 `Next step` (form factor +
Beta-broker-first contract). The recommended first build is the Alpha + Beta
slice inside the `makerspace` skill behind a provider-agnostic quote contract.
