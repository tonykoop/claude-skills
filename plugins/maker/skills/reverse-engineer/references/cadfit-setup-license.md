# CADFit Setup, Runtime, And License Gate

Use this reference before enabling any CADFit-backed `maker:reverse-engineer` mesh/scan workflow. CADFit is an optional third-party research dependency, not bundled code in this public skill.

## License Gate

Source checked: `https://github.com/ghadinehme/CADFit` on 2026-06-20.

Gate result: **flagged, do not vendor CADFit code into this repo by default.**

- CADFit is released under **Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)**.
- The upstream README says the code is free for academic and research use and points to the `LICENSE` file.
- The CC BY-NC 4.0 license permits sharing/adaptation only for NonCommercial purposes and requires attribution.
- The CC license text says patent and trademark rights are not licensed.
- The upstream README says a provisional patent application has been filed for the CADFit method and directs commercial licensing inquiries to `ghadi@mit.edu`.

Practical rule for this public skill:

- OK: document CADFit as an optional external tool; detect whether a local user-installed CADFit environment is available; emit setup guidance; keep all CADFit source outside the skill package.
- Not OK without legal/commercial permission: copy CADFit source, weights, substantial code, or modified CADFit files into `claude-skills`; present the public skill as commercially licensed CADFit redistribution; imply patent rights are granted.

## Attribution

When CADFit is mentioned in outputs or docs, include:

- CADFit: Precise Mesh-to-CAD Program Generation with Hybrid Optimization.
- Ghadi Nehme, Eamon Whalen, and Faez Ahmed.
- ICML 2026 / arXiv:2605.01171.
- Upstream repository: `https://github.com/ghadinehme/CADFit`.
- License: CC BY-NC 4.0, with upstream patent notice.

## Install Sketch

Install CADFit outside this skill, in a user-controlled environment:

```bash
git clone https://github.com/ghadinehme/CADFit.git
cd CADFit
conda create -n cadfit-env python=3.10
conda activate cadfit-env
pip install -r requirements.txt
```

Upstream quick-start command:

```bash
python run_pipeline.py <input_folder>
```

Primary native/runtime dependencies from upstream:

- Python 3.10
- CadQuery 2.6.1
- cadquery-ocp 7.8.1.1.post1 / OpenCascade
- manifold3d, trimesh, pymeshlab, scipy, shapely, scikit-learn, rtree, networkx
- optional image/sketch filtering stack: torch, PyVista/off-screen renderer, Pillow, HuggingFace Hub

## Runtime Availability Matrix

| Host | CADFit kernel status | Skill behavior |
|---|---|---|
| Local workstation with conda, native deps, and mesh files | Supported if user installs CADFit externally | Run optional CADFit wrappers against local paths |
| Headless Linux with OpenCascade/CadQuery available | Possible but fragile | Treat kernel failures as normal scoring signals |
| Codex CLI sandbox without native deps | Usually unavailable | Degrade to observation ledger and setup instructions |
| Mobile / zip-uploaded skill host | Unavailable | Do not attempt CADFit execution |
| Vision-less text runtime | Unavailable unless mesh path is supplied and kernel exists | Stay in description-only or mesh-metadata mode |
| Photo-only intake without watertight mesh | Out of CADFit scope | Do not promise CADFit; request mesh/scan or route to normal reverse-engineer workflow |

## Scope Boundary

CADFit belongs only to the `real scan/mesh already exists` branch. It should never weaken the existing reverse-engineer discipline for photos, sketches, named objects, or dictated descriptions.
