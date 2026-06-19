# Civic-Minded Studio Pipeline — benevolence reward, robotic charity, gilds of craft

A forward-looking governance-design sketch for [claude-skills#234](https://github.com/tonykoop/claude-skills/issues/234).
Status: **capture / far-horizon.** Captured for the inbox as a governance design
principle, not yet scoped work; this doc is the first scoping pass. Pairs with
the humanoid maker-team architecture ([#232](../humanoid-maker-team/README.md))
and the autonomous-org orchestration story in StudioPipeline Epic #66.

## The thesis

At functional post-scarcity — an automated sales/manufacturing/media pipeline
plus a humanoid team meeting all material needs — continued financial growth is
an arbitrary scorecard. The design choice is whether the orchestrator's
objective keeps maximizing surplus (oligarch mode) or **radiates surplus
capability outward** (gilds-of-craft mode). This RFC argues for the latter as an
explicit, encoded objective, and sketches how.

## The re-engineered reward function

The core lever is the orchestrator's master optimization. Replace
profit-maximization with a weighted civic objective:

```
Reward = α · Sustainability
       + β · Creative_Output
       + γ · Community_Impact
```

So casting/marketing agents scout local community bottlenecks with the same
urgency and prestige as a high-ticket launch. Sketch of the terms:

| Term | Proxy metric | Notes |
|---|---|---|
| `Sustainability` | abundant-atom material share, energy/job, waste reclaimed | reuses the scarcity gate from [#205](../manufacturing-capability-index/README.md) |
| `Creative_Output` | count/novelty of validated finished goods | leans on a real verification gate, not self-report |
| `Community_Impact` | outreach blocks delivered, assets lent, people served | needs a consented, auditable impact ledger |

The weights `α, β, γ` are governance knobs set by the human owner, not the
agents — and they are an **immutable-by-agents** config (same posture as the
governance layer's deploy barriers): an autonomous org must not be able to
quietly rewrite its own civic objective toward self-enrichment.

## Three civic mechanisms

### 1. Decentralized robotic charity

Deploy operational *capability*, not just money: micro-manufacture open-source
custom-fit prosthetics / pediatric wheelchairs at near-zero marginal cost;
schedule **Community Outreach Blocks** (a "1st-AD" scheduling agent) when channels
run ahead of schedule — repair housing, fix plumbing, install solar for
low-income/elderly neighbors.

### 2. Capacitive microloans (humanoid renting)

Lend autonomous hardware assets: an aspiring artisan borrows two humanoids + a
portable CNC rig for a month, arriving with skeletal-modeling skills pre-loaded,
to build initial inventory and a storefront toward financial sovereignty. The
loan is of *productive capacity*, repaid in output or returned, not a cash debt.

### 3. Gilds of craft, not oligarchy

When the factory fits in a garage and the labor force is an open-source humanoid
team, scaling no longer requires exploiting labor or hoarding resources, so the
wealth gap stops compounding. Success is measured by abundance radiated outward —
every neighborhood workshop a localized powerhouse of mutual aid.

## Guardrails (why a civic reward still needs limits)

A benevolence objective is not self-justifying; encode the limits explicitly:

- **Consent & dignity** — outreach and "impact" require recipient consent; no
  unrequested intervention. The impact ledger records consent, not just delivery.
- **Safety gate stays hard** — civic work crosses physical-world boundaries
  (housing repair, electrical/solar); the human-signoff barrier from the
  governance layer applies before any deploy, charity or not.
- **No labor-undercutting harm** — lending free capacity into a community can
  displace local paid tradespeople; the objective should weight *additive* work
  (unmet need) over substituting for existing livelihoods.
- **Anti-gaming** — `Community_Impact` is the easiest term to fake; it must be a
  verified, consented ledger, adversarially audited like any other gate.

## Open questions

- How is `Community_Impact` measured without it becoming a vanity metric?
- Who sets and audits `α, β, γ`, and how is that authority kept human-held?
- Does "capacitive microloan" need a legal/liability wrapper before any real
  hardware leaves the shop?

## Scope

Far-horizon governance RFC. No code — this names the reward shape, the three
mechanisms, and the guardrails so the autonomous-org layer has a stated civic
design principle to build toward. Natural long-term home is the StudioPipeline
ecosystem (Epic #66).
