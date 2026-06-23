# End-to-End Multimedia Release Hook Contract

**Epic:** #471 — playlist-builder audio-dynamic  
**Story:** #476  
**Version:** v1.0  

---

## Overview

The release hook closes the movement→audio pipeline into a single *release bundle*: a
timestamped directory containing the choreography script, the audio mix plan, and a
provenance block. The bundle can then be handed off to StudioPipeline for publication.

`release_hook.py` implements this compilation step. It is the last stage in the epic #471
pipeline: `movement_bridge → release_hook → StudioPipeline`.

---

## Inputs

| Input | Type | Description |
|---|---|---|
| `mix_plan` | `MixPlan` dict or object | Output of `movement_bridge.build_mix_plan()` |
| `choreo_script_path` | path or string | Path to the choreography script (Markdown) |
| `output_dir` | path or string | Directory where the bundle is written |

---

## Output — Release Bundle

`compile_release()` writes three files to `output_dir/`:

### `choreo_script.md`

A copy of the choreography script. Content is unchanged; copied verbatim.

### `audio_mix_plan.json`

The `MixPlan` serialised to JSON. Fields:

```jsonc
{
  "routine_id": "hip-hop-demo-001",
  "style": "hip-hop",
  "total_duration_s": 480,
  "blocks": [
    {
      "name": "Warm-up",
      "bpm_target": 80,
      "duration_s": 120,
      "kinetic_texture": null,
      "peak_count_s": null,
      "candidates": [...],
      "anchor_offset_s": 0.0,
      "anchor_fallback": true
    },
    ...
  ]
}
```

### `provenance_block.json`

An IP-timestamp block attached to the release for offtheshelf provenance tracing:

```jsonc
{
  "routine_id": "hip-hop-demo-001",
  "generated_at": "2026-06-22T18:30:00Z",   // ISO-8601 UTC
  "choreo_script_sha256": "a3f5...",          // SHA-256 of choreo_script.md content
  "audio_mix_plan_sha256": "bb12...",         // SHA-256 of audio_mix_plan.json content
  "epic": "tonykoop/claude-skills#471",
  "skill_version": "playlist-builder/release-hook@1.0.0"
}
```

---

## StudioPipeline Handoff

When the environment variable `STUDIOPIPELINE_HOOK_URL` is set, `compile_release()` sends
the bundle metadata to the pipeline after writing the files. The handoff is **non-blocking**:
if the hook URL is absent or the request fails, compilation succeeds and a warning is printed.

Handoff payload (HTTP POST, JSON):

```jsonc
{
  "routine_id": "...",
  "bundle_dir": "/abs/path/to/output_dir",
  "provenance": { ... },   // the provenance_block dict
  "source": "playlist-builder/release-hook@1.0.0"
}
```

The pipeline is expected to pick up `choreo_script.md` and `audio_mix_plan.json` from the
bundle directory. This matches the StudioPipeline output-stage contract (see `docs/deploy_bridge.md`).

---

## IP Timestamp Format

The `generated_at` field uses ISO-8601 with UTC timezone (`Z` suffix). The `sha256` fields are
lowercase hex strings of the SHA-256 digest of the *file content as written to disk* (UTF-8,
no BOM, Unix line endings).

The provenance block is the minimal offtheshelf footprint required by clause 4 of the Book of
Movement Primitives provenance spec (offtheshelf #35). Adding a richer provenance record is
left to StudioPipeline.

---

## Error Handling

| Condition | Behaviour |
|---|---|
| `choreo_script_path` does not exist | `FileNotFoundError` raised before any files are written |
| `output_dir` does not exist | Created automatically (including parents) |
| `mix_plan` is a dict | Accepted directly; `to_dict()` is called if it's a `MixPlan` object |
| `STUDIOPIPELINE_HOOK_URL` absent | Skips hook silently |
| Hook HTTP failure | Prints warning; does not raise |
