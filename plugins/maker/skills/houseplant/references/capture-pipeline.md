# Capture Pipeline

Read this reference when the user has phone captures (photos, photogrammetry scan, orbit video, or lazy-susan video) and wants them turned into a Blender-usable twin, or when the user asks how to capture a specimen well in the first place. Pair with [`blender-digital-twin.md`](blender-digital-twin.md) for the actual scene work.

## Why This Matters

Garbage capture leads to garbage twins. Wire-gauge math, prune-projection silhouettes, and bite-in timelines only mean something if the twin is the right size and the right shape. Spend a few minutes on capture so the rest of the workflow earns its keep.

## Pick the Capture Mode

Pick the lightest mode that meets the user's goal. Heavier modes are not better when the user only wants to plan a structural prune.

| Mode | Best when | Output | Twin quality |
|---|---|---|---|
| Multi-angle photos + ruler | The user only wants pruning markup on photos plus a stylized procedural twin; lighting is good; specimen is too delicate to handle. | JPG/PNG set | Stylized: L-system or curve sketch driven by photo measurements. |
| Photogrammetry scan (Polycam / Luma / RealityScan) | The user wants a real digital twin with their plant's actual trunk and root flare; lighting is even; subject is non-reflective. | `.obj` / `.ply` / `.glb` + texture | Hybrid: scanned trunk, procedural foliage. |
| Orbit phone video | The user wants a scan but doesn't have a photogrammetry app, or has motion artifacts in still photos. | `.mp4` / `.mov` | Same as photogrammetry after frame extraction. |
| Lazy-susan stabilized video | The user has a small specimen that can be safely rotated; tripod-stabilized phone is easier than walking. | `.mp4` / `.mov` on a turntable | Often the cleanest input — controlled lighting + steady camera. |

When in doubt, ask the user which they have time for and walk them through that mode only. Don't demand the heaviest option.

## Required Captures

### Mode A: Multi-angle photos + ruler

Minimum useful set:

- Front (chosen design front of the bonsai).
- Back.
- Left side.
- Right side.
- Top-down (canopy plan view).
- Trunk and root-flare close-up.
- One close-up per target branch the user wants to discuss.
- **One photo with a ruler held in the plane of the trunk**, parallel to the camera sensor, with both ends of a known segment visible. This is the scale reference. A credit card or any object of known dimensions also works; document what was used.

Ask the user to keep camera height roughly at the plant's mid-canopy and shoot orthographic-ish (camera pointed at the plant, not tilted up or down). This makes corresponding branches easier to identify across views.

### Mode B: Photogrammetry scan

Minimum useful set:

- Two orbit passes (upper canopy and lower trunk/roots) at different heights so the scan doesn't miss the underside of the canopy or the root flare.
- Even, diffuse lighting. Direct sun or hard backlight wrecks the reconstruction on glossy leaves.
- One reference photo with a ruler or known object held against the trunk for scale validation after the scan is built.
- Static plant (no breeze; pause HVAC if indoors).

Output: an `.obj` / `.ply` / `.glb` plus texture. Import to `00_source_scan/` per the scene contract.

### Mode C: Orbit phone video

Minimum useful set:

- 30–60 second walk-around at near-constant distance, near-constant height (lower orbit), then a second 30 second pass higher.
- Same lighting requirements as Mode B.
- One frame with a ruler visible for scale.

Convert to frames before feeding to a photogrammetry pipeline (ffmpeg one-shot in `scripts/`-style note below). 1 fps is usually enough for a slow orbit; 2 fps for faster orbits.

### Mode D: Lazy-susan stabilized video (often Tony's preferred mode)

Minimum useful set:

- Plant on a lazy susan; phone on a tripod at fixed height; rotate the plant 360° slowly (45–60 seconds).
- Then raise the phone tripod and repeat for the upper canopy.
- Then lower it and repeat for root flare/nebari.
- Ruler taped to the plant pot at known orientation OR held in one frame against the trunk during the orbit.
- Use a single, soft light source positioned off-axis so shadows rotate with the plant, not with the camera — this is critical for photogrammetry quality on a turntable.

This mode tends to produce the cleanest scans because the plant moves as a rigid body relative to the lights, the way photogrammetry math expects.

## Scale Calibration (Ruler Workflow)

Once a scan is imported to Blender, derive scene scale from the ruler before anything else:

1. Identify the same ruler segment in two frames (or in the reconstructed mesh) and pick two endpoints whose real distance you know (e.g., the 0 cm and 10 cm marks).
2. In Blender, snap the 3D cursor or two empties to those endpoints on the imported mesh.
3. Measure the current distance between them in Blender units.
4. Compute a scale factor `desired_real_meters / current_blender_distance`.
5. Apply uniform scale to the parent collection and `apply_scale` so descendants inherit it cleanly.

`scripts/scale_from_ruler.py` does the math given two coordinates and a known real distance. The user should still eyeball-check by comparing pot diameter or another known object against the scaled scene.

If no ruler is in the scene, fall back to a known pot/planter diameter the user can report — it's noisier but better than nothing. State the uncertainty in the digital-twin sync log.

## When the Scan is Bad

Photogrammetry often turns thin Ficus leaves into a fused green blob. That is fine and expected. The plan:

- Keep the scanned trunk and primary branches — they're usually accurate.
- Discard the scanned foliage geometry and replace it with procedural or instanced leaves bound to the extracted branch curves (see `blender-digital-twin.md` → "Geometry node overwrite").
- If even the trunk scan is poor, drop back to Mode A and build a curve-only stylized twin. State this clearly in the sync log so the user doesn't think the twin is a precise representation.

## Video → Frames Helper

A typical ffmpeg-style invocation the user can run from their machine (Claude should not invent paths; ask first):

```bash
ffmpeg -i orbit.mp4 -vf "fps=1" frames/frame_%04d.jpg
```

For lazy-susan video where the plant rotates evenly, 1 fps per 360° orbit gives ~45 frames at a 45-second pass, which is plenty for most photogrammetry apps.

## Output Contract for Capture Sessions

When a capture session ends, append to the plant record:

```markdown
### YYYY-MM-DD - captured
- Mode:
- Files saved to:
- Scale reference used:
- Lighting / conditions:
- Known issues with the capture:
- Twin status after import:
- Follow-up:
```

This is what makes capture data reusable months later when the user is comparing growth.
