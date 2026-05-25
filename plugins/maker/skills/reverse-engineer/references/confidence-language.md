# Confidence Language

Use confidence language to protect uncertainty. Confidence is about the claim, not the agent's tone.

## Claim Types

- `observed`: directly visible in the provided evidence or explicitly shown in a photo/video.
- `measured`: supplied by the user, read from a scale, or computed from a reliable reference in the same plane.
- `inferred`: reasoned from evidence, common construction patterns, physics, proportions, or comparable objects.
- `assumed`: temporarily chosen to continue analysis; not evidenced enough to rely on.
- `unknown`: needed information that current evidence cannot provide.

## Confidence Levels

| Level | Use when | Required wording |
| --- | --- | --- |
| High | Directly visible, measured, or strongly constrained by multiple independent cues. | "High confidence because..." |
| Medium | Plausible and supported by evidence, but alternatives remain. | "Medium confidence; the main alternative is..." |
| Low | Weakly suggested, perspective-limited, or based on analogy. | "Low confidence; treat as a placeholder until..." |
| Unknown | Current evidence cannot support a claim. | "Unknown from current evidence." |

## Good Phrases

- "The photo shows..."
- "The user-provided measurement is..."
- "I infer this from..."
- "A reasonable working assumption is..."
- "This remains unknown because..."
- "Builder-critical unknown:"
- "Not enough evidence to claim..."
- "Use this as an estimate, not a fabrication dimension."
- "This can move to high confidence after..."

## Phrases To Avoid

- "Clearly" for hidden mechanisms or materials.
- "Obviously" for any inferred construction.
- "Definitely" unless the claim is measured or directly visible.
- "Exact" for image-derived dimensions without a calibrated scale and perspective control.
- "Looks like X, so it is X."
- "Builder-ready" when critical dimensions are still assumptions.

## Dimension Wording

- Use ranges for image-derived dimensions unless a reliable scale reference exists.
- State the source plane: "estimated in the same plane as the ruler" or "not in the same plane, so perspective error may be large."
- Separate nominal target from tolerance: "Target 25 mm; tolerance unknown" is better than a naked "25 mm."
- For proportional estimates, say "about 0.42x the overall length" instead of inventing absolute units.

## Cap on Dimensional Confidence Under Degraded Intake

When the observation ledger's `intake.image_access_mode` is `description-only`, `missing`, `partial`, or `named-object`, dimensional and material claims are capped:

| Claim subject | Max confidence | Notes |
| --- | --- | --- |
| Absolute dimension (mm/in/g/etc.) | `low` | Even if the value matches a class average, no `medium` or `high` without a measurement or direct image. |
| Proportion or ratio | `medium` | Topology and proportions can survive prose. State the source plane and the prose phrase that justifies it. |
| Material (specific species/alloy/grade) | `low` | "Looks like oak" from prose stays low. Class-typical material is `inferred + low`, never `observed`. |
| Material class (wood / metal / plastic / fabric) | `medium` | Function and feel from prose can usually rule a class in or out. |
| Mechanism topology | `medium` | "It hinges at the back" from prose can be `inferred + medium` if the prose is unambiguous. |
| Color / finish exact | `low` | "Dark stain" stays a category, not a Pantone/RAL/wood-species commitment. |

The cap applies to *new* claims derived from the degraded source. User-supplied measured values, named-class data with a cited authoritative source, or claims later confirmed by a direct-mode follow-up image are exempt and may be `high`.

When the cap forces a downgrade, say so explicitly: "Capped at low confidence under degraded intake mode (description-only). Move to medium/high after a direct-mode image or measurement."

## Confidence Note Pattern

```text
Claim: [specific claim]
Type: observed / measured / inferred / assumed / unknown
Confidence: high / medium / low / unknown
Evidence: [photo, measurement, visible cue, comparable part, physics]
Risk if wrong: [builder, safety, performance, cost, legal]
Verification: [photo, measurement, test, teardown, supplier spec]
```
