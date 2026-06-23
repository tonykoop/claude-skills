# Motion Primitives Import Seam

<!-- TODO: Replace stub with live import from tonykoop/offtheshelf#35 when published -->

## Status

**STUB — offtheshelf#35 not yet published.**  
This seam is implemented but points to the inline domain JSON files until heidi's `tonykoop/offtheshelf#35` (Book of Movement Primitives) publishes its schema.

When #35 lands, the migration path is:
1. Confirm the published schema matches the expected schema below
2. Replace `domains/*.json` primitive arrays with a loader that fetches from the offtheshelf package
3. Remove this stub notice

## Expected schema (target for offtheshelf#35)

The sequencer expects each domain JSON file to follow this schema. The domain files in `domains/` are hand-authored against this contract so the swap is a file replace.

```json
{
  "schema_version": 1,
  "domain": "<string>",
  "clock": {
    "type": "beat | breath",
    "bpm_range": [90, 110],
    "count_unit": 8,
    "breaths_per_minute": 12
  },
  "objective": "style_expression | breath_alignment | force_output | joint_safety",
  "requires_clinical_review": false,
  "primitives": [
    {
      "id": "<kebab-case-string>",
      "name": "<human-readable name>",
      "description": "<optional prose>",
      "weight_shift": "left | right | bilateral | unweighted",
      "facing": "north | south | east | west | any",
      "tempo_class": "slow | medium | fast",
      "energy_delta": 0.0,
      "duration_beats": 4,
      "valid_next": ["<id>", "..."]
    }
  ]
}
```

## Coordinate schema shape via GitHub

If heidi's ontology diverges from this schema, open a comment on `tonykoop/offtheshelf#35` with the delta and update this file with the agreed resolution before merging #35 support here.

## Loader stub

```python
# TODO(offtheshelf#35): replace with real loader
def load_primitives_from_offtheshelf(domain: str) -> dict:
    raise NotImplementedError(
        "offtheshelf#35 not yet published. "
        "Use domains/*.json inline files until the ontology ships."
    )
```
