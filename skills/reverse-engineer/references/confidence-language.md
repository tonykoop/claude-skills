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

## Image-Access Confidence Ceilings

When `image_access_mode` is `description-only`, no claim about absolute dimensions, colors, surface finish, material, fastener type, wear, damage, or hidden construction may exceed `low` confidence unless it is supplied as a user measurement. Topology and named features from the user's prose may reach `medium` when the wording is explicit, but mark the evidence as `observed-by-user`, not analyst-verified.

When `image_access_mode` is `missing`, do not analyze visual facts. Ask for recovery or explicit approval to continue from class knowledge or prose. Any class-knowledge claim is `inferred` and capped at `low` unless independently sourced or measured.

When `image_access_mode` is `partial`, confidence only applies to the evidence actually visible. Claims about missing views, occluded regions, or sibling images inherit the `description-only` ceiling.

## Confidence Note Pattern

```text
Claim: [specific claim]
Type: observed / measured / inferred / assumed / unknown
Confidence: high / medium / low / unknown
Evidence: [photo, measurement, visible cue, comparable part, physics]
Risk if wrong: [builder, safety, performance, cost, legal]
Verification: [photo, measurement, test, teardown, supplier spec]
```
