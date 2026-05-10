# Builder Handoff Template

Use this only when the builder-ready gate passes or when the user explicitly wants a provisional prototype plan. Label provisional handoffs clearly.

## Handoff Header

```text
Project:
Source evidence:
Image access mode: direct / file-path / partial / description-only / missing
Source qualifiers: analyst-verified / file-verified / partial-verified / observed-by-user / not-provided
Goal:
Target skill: maker-engineering / makerspace / instrument-maker-v4
Handoff status: builder-ready / provisional / blocked
Date:
```

If `Image access mode` is `description-only` or `missing`, default `Handoff status` to `provisional` or `blocked`. Use `builder-ready` only when independent measurements, verified files, or explicit user confirmation retire builder-critical unknowns.

## Summary

- **What this is:** Object, mechanism, instrument, artifact, or subsystem being analyzed.
- **What the builder should make:** Replacement, inspired variant, repair part, fixture, prototype, commissioned spec, or instrument packet.
- **What must remain unchanged:** Fit, interface, acoustic behavior, look, ergonomics, safety requirement, or user priority.
- **What may change:** Materials, process, finish, dimensions, tooling, scale, or feature simplifications.

## Evidence Ledger

| Claim | Type | Confidence | Evidence | Builder impact |
| --- | --- | --- | --- | --- |
|  | observed / measured / inferred / assumed | high / medium / low | Include source qualifier: analyst-verified, file-verified, partial-verified, observed-by-user, or not-provided | critical / useful / non-critical |

## Critical Dimensions

| Feature | Value or range | Units | Source | Tolerance | Confidence | Notes |
| --- | --- | --- | --- | --- | --- | --- |
|  |  |  | measured / inferred / assumed |  |  |  |

## Materials and Process

| Part / region | Likely material | Evidence | Acceptable substitute | Process notes | Confidence |
| --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |

## Mechanism / Construction

- **Working hypothesis:**
- **Functional interfaces:**
- **Motion or force path:**
- **Assembly order:**
- **Failure modes to test:**

## Unknowns Carried Forward

| Unknown | Builder risk | Prototype-safe workaround | Verification plan |
| --- | --- | --- | --- |
|  |  |  |  |

## Routing Notes

Use this routing language:

- To `maker-engineering`: "Please convert this analysis into engineering requirements, tolerances, trade studies, and a prototype validation plan."
- To `makerspace`: "Please convert this analysis into shop-ready fabrication steps, fixtures, tools, material purchasing, and safety checks."
- To `instrument-maker-v4`: "Please convert this validated instrument analysis into an instrument build packet, preserving acoustic unknowns and measurement confidence."

## Blocked Handoff Note

If the gate fails, do not write a full builder handoff. Use:

```text
Handoff status: blocked
Reason:
Builder-critical unknowns:
Minimum measurements/tests needed:
What can be done now:
```
