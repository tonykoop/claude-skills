# Rosetta Parallel Dataset Trainer

Use this reference when building or reviewing shorthand-to-transcript pairs. The Rosetta dataset is a parallel corpus: each row links one shorthand span to the live voice transcript from the same moment.

## Pair Format

Each class file is JSON with this shape:

```json
{
  "class_id": "class-YYYY-MM-DD-slug",
  "source": "private corpus reference or local capture id",
  "pairs": [
    {
      "id": "pair-001",
      "shorthand": "DD // 5B",
      "transcript": {
        "start_sec": 0,
        "end_sec": 45,
        "text": "Settle into the breath and notice the space between effort and ease."
      },
      "human_review": {
        "status": "pending",
        "reviewer": "",
        "notes": ""
      }
    }
  ]
}
```

Required fields:

- `id`
- `shorthand`
- `transcript.start_sec`
- `transcript.end_sec`
- `transcript.text`
- `human_review.status`

## Extracted Labels

The public trainer extracts:

- `somatic_spacing`: seconds, rough breath counts, and seconds per parsed pose token
- `structural_transitions`: adjacent pose-token moves such as `DD -> RLH -> CL`
- `thematic_infusion_points`: transcript spans containing theme, intention, attention, breath, space, or feeling-language cues
- `token_count`, `pose_tokens`, `operator_tokens`, and `draft_tokens`

## Quality Bar

Rosetta output is not trusted automatically. A class export is considered trainable only when:

- every pair parses with zero draft tokens under the configured strictness
- every transcript span has positive duration and non-empty text
- the class has at least one structural transition
- the class has at least one thematic-infusion point or is explicitly marked as intentionally theme-light
- every pair has `human_review.status = "approved"` with a reviewer name

If any gate fails, the trainer returns `trusted_for_training = false` and lists the required fixes. This keeps shorthand decoding and future voice-style generation under human review instead of autopilot.
