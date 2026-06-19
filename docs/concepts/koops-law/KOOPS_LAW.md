# Koop's Law — an Adaptive Manufacturing Scaling Law

> `C = k · (S_e)^α`

A visionary RFC for [claude-skills#204](https://github.com/tonykoop/claude-skills/issues/204).
Status: **capture / forward-looking**. This is a thesis, not a finished claim —
its job is to state the hypothesis precisely enough that MakerBench-HWE can later
try to *falsify* it.

## The one-paragraph thesis

Moore's Law indexed capability to *time*. Wright's Law indexed cost to
*cumulative production* (every doubling of units made drops cost a fixed
percentage). **Koop's Law** proposes that physical-manufacturing capability
scales not with time and not with raw unit count, but with **Evaluated Spatial
Complexity** — the cumulative volume of programmatically-graded,
*physically-verified* geometric variation a system has actually built and
measured. Each doubling of `S_e` advances multi-material manufacturing
automation by a fixed efficiency increment `α`. MakerBench-HWE is positioned as
the **fitness function** that measures the curve: it is the instrument, not just
a leaderboard.

## Terms

### Capability `C`

A scalar capability index assembled from the [Manufacturing Capability Index
(#205)](../manufacturing-capability-index/README.md): for a given process and
era, how small a feature, how large an envelope, how tight a tolerance, across
how many materials/states, a system can *reliably and verifiably* produce. `C`
is the dependent variable Koop's Law predicts.

### Evaluated Spatial Complexity `S_e`

The independent variable, and the load-bearing definition. `S_e` is **not** how
many parts were made — it is how much *graded, physically-verified geometric
variation* has been accumulated. A useful first decomposition:

```
S_e  ≈  Σ over verified builds of  ( geometric_information × verification_fidelity )
```

- **geometric_information** — a complexity measure of the produced geometry
  (e.g. distinct feature classes, DOF of the toolpath, material/state
  transitions), not its bounding-box size. A 200-feature multi-material part
  carries far more than a scaled-up cube.
- **verification_fidelity** — how rigorously the result was measured against the
  intent (visual only → dimensional → functional → destructive). Unverified or
  simulation-only builds contribute ~0; this is what keeps `S_e` honest and is
  exactly the discipline MakerBench's grader enforces.

`S_e` deliberately counts **evaluated** complexity: a million unmeasured prints
move the curve far less than a thousand graded, multi-material, tolerance-checked
ones. That is the whole point — learning comes from measured feedback, not motion.

### The learning-rate coefficient `α`

`α` is a *physical* learning-rate exponent: the elasticity of capability with
respect to evaluated complexity. `α > 0` means capability compounds as graded
variation accumulates. In log space the law is linear and `α` is just a slope:

```
log C  =  log k  +  α · log S_e
```

so fitting `α` is an ordinary-least-squares slope on `(log S_e, log C)` points —
which is precisely why it needs a leaderboard that emits both axes.

## How a physically-verified leaderboard measures `α`

This is the part that makes Koop's Law an empirical claim rather than a slogan:

1. **Every graded challenge emits an `S_e` increment** — the geometric
   information of the submitted-and-verified design times its verification
   fidelity. Only the **physically/programmatically verified** portion counts
   (a fabricated or simulation-only result adds nothing), so the index cannot be
   gamed by submitting volume.
2. **Periodically snapshot `C`** from the capability frontier the leaderboard has
   demonstrated (min feature achieved, tolerance held, materials/states crossed),
   reusing the #205 row fields that are *gateable today*.
3. **Regress** `log C` on `log S_e` across snapshots; the slope is `α`, the
   intercept is `log k`. A stable positive `α` across eras is the evidence; a
   flat or noisy fit falsifies the law.

The companion [#205 index](../manufacturing-capability-index/README.md) supplies
the dynamic constraint boundary `C` is read from, so the two captures are a pair:
#205 is the ruler, #204 is the law that says how fast the ruler moves.

## Lineage

| Law | Independent variable | Mechanism |
|---|---|---|
| Moore's Law | time | transistor density doubling |
| Wright's Law | cumulative units produced | learning-by-doing cost decline |
| **Koop's Law** | evaluated spatial complexity `S_e` | learning-by-*grading* capability gain |

Koop's Law is Wright's Law's learning curve relocated from *cost-per-unit* to
*capability-per-evaluated-complexity*, with the grader as the source of truth.

## Kardashev framing (the civilizational stakes)

If `S_e` keeps doubling and `α` holds, the curve documents a *physical*
intelligence explosion: AI designing the hardware that lets the next, more
capable AI exist. Mapped onto the Kardashev scale, that is the Type 0 → Type I
transition — a civilization moving from "best material in a vacuum" design to
resource-aware mastery of matter and energy (the states-of-matter and scarcity
gates of #205 are the early guardrails). MakerBench-HWE, in this framing, is the
seismograph for that transition.

## Falsifiability & open questions

- **Is `S_e` measurable without circularity?** The geometric-information and
  verification-fidelity terms need concrete, reproducible operationalizations
  before `α` means anything. This is the first real work, and it lives in the
  #205 index + the MakerBench grader, not in this doc.
- **Is the relationship a power law at all?** It might be logistic (an S-curve
  with a ceiling) rather than an unbounded power law. The regression above is
  also the test of *which* model fits.
- **Does `α` vary by material/process family?** Likely yes — there may be a
  family of `α`s, not one. That is a finding, not a flaw.

## Scope

Forward-looking RFC. No code, no measured `α` yet — the measurement apparatus
(#205 index + MakerBench grader emitting `S_e` and `C`) must exist first. Natural
long-term home is `makerbench-hwe`; it lives here as the thesis so the rest of
the MakerBench effort has a stated north star to build the instrumentation
toward.
