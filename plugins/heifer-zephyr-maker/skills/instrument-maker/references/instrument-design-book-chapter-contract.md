# Instrument Design-Book Chapter Contract

This reference defines the public design-book / yearbook chapter scaffold for
instrument repos. It is intentionally a contract, not a rollout instruction:
one L2+ pilot must prove the scaffold before any batch chapter generation.

## Purpose

Create public-facing chapters that explain an instrument project without
overstating the underlying build evidence. The chapter can be beautiful, but it
must remain traceable to the source instrument packet.

## Non-goals

- Do not imply every instrument repo is ready for a polished public chapter.
- Do not promote concept imagery into evidence for fit, tuning, safety, or
  manufacturability.
- Do not import large media before Git LFS rules are committed.
- Do not close the original Round 9 capture until the scaffold and one pilot
  are proven. Use `Refs #100` in downstream work.

## Readiness Mirror

Public chapter readiness mirrors source instrument readiness. The chapter's
banner, claims, and visual treatment must use the most conservative source
state that still applies.

| Source readiness | Chapter allowance | Required banner |
|---|---|---|
| L0 Concept | No public chapter. Keep the work in the idea inbox or private planning notes. | N/A |
| L1 Design | Private or draft outline only. No polished image-gen-2 chapter imagery and no shop-readiness claims. | `L1 Design - not shop-ready` |
| L2 Shop Packet | One pilot scaffold may be created for careful builder/publication review. Generated imagery must be labeled as concept/supporting imagery and must not imply build-ready status. | `L2 Shop Packet - not build-ready` |
| L3 Validated Packet | Chapter may claim build-ready only when packet validator, generated/rendered artifacts, unit checks, sourceability, and tolerance checks are cited. No empirical/measured claims yet. | `L3 Validated Packet - build-ready evidence available` |
| L4 Empirical Packet | Chapter may include measured build feedback, tuning deviations, correction-loop results, catalog feedback, build photos, and generated supporting imagery with source links. | `L4 Empirical Packet - measured feedback available` |

If the source packet regresses or a verifier flags unresolved safety, tuning,
IP, provenance, or fabrication concerns, the chapter readiness must regress too.

## Chapter File Shape

The first downstream scaffold in `tonykoop/instrument-maker` should create a
reusable folder shape like this:

```text
chapters/<instrument-slug>/
  README.md
  chapter.md
  assets/
    asset-ledger.csv
    lfs-policy.md
  prompts/
    prompt-appendix.md
  images/
    generated/
    source/
  audio/
  drawings/
```

The exact folder names may change to match the downstream repo, but the
contract pieces must remain present.

## Chapter Template

Each `chapter.md` starts with a readiness banner:

```markdown
> Readiness: <L1/L2/L3/L4 label>
> Source packet: <repo path, issue, or commit>
> Evidence boundary: <what is measured / built / inferred / generated>
> Generated media: <none / concept only / supporting labeled imagery>
```

Then include:

1. `Instrument story` - what the instrument is and why it exists.
2. `Design evidence` - links to source packet, drawings, validation, and build
   logs. Claims must point to source evidence.
3. `Making notes` - materials, process, and known constraints.
4. `Visual plate` - photos, drawings, or generated images, each linked to the
   asset ledger.
5. `Sound / notation` - optional. Route to `sheet-music` when notation,
   playable examples, fingering diagrams, MusicXML, ABC, LilyPond, or rendered
   score assets are needed.
6. `Status and next gate` - the next readiness gate before publication or
   before adding sibling chapters.

## Asset Ledger

Every media asset used by the chapter gets one row in
`assets/asset-ledger.csv`:

```csv
asset_path,asset_type,source,license_or_owner,created_or_modified,readiness_claim,generated,model_or_tool,prompt_id,notes
images/source/body-front.jpg,photo,build log commit <sha>,Tony Koop,2026-05-10,L4 empirical build evidence,false,,,"unmodified source photo; measured feedback cited separately"
images/generated/hero-concept-01.png,image-gen-2,prompt appendix P001,Tony Koop,2026-05-10,L2 concept/support only,true,image-gen-2,P001,"not dimensional or build-ready evidence"
drawings/top-plate.svg,drawing,source packet drawings/top-plate.svg,Tony Koop,2026-05-10,L2 shop-packet artifact,false,,,"derived from packet drawing; not validated/build-ready until L3"
```

The ledger separates source photos, technical drawings, generated imagery,
audio, PDFs, and showcase exports. Public copy may use source-evidence rows for
factual claims. Generated rows can support mood, assembly context, layout, or
visual explanation, but not dimensions, tuning claims, safety claims, or build
completion claims.

## Prompt Appendix

`prompts/prompt-appendix.md` records every generated-image prompt and edit chain:

```markdown
## P001 - Hero concept plate

- Model/tool: image-gen-2
- Source evidence: <source packet path or "none">
- Prompt: <final prompt text>
- Negative constraints: no fake measurements; no unlabeled logos; no implied
  build-ready status unless source packet is L3+; no implied measured or
  empirical feedback unless source packet is L4
- Output assets:
  - `images/generated/hero-concept-01.png`
- Label to display: Generated concept image, not dimensional evidence.
```

If an image is derived from a real build photo, record the source asset and the
edit instruction. If an output is fully synthetic, say so.

## Git LFS Policy

Commit `.gitattributes` before importing large media. The downstream scaffold
should include at least:

```gitattributes
*.png filter=lfs diff=lfs merge=lfs -text
*.jpg filter=lfs diff=lfs merge=lfs -text
*.jpeg filter=lfs diff=lfs merge=lfs -text
*.webp filter=lfs diff=lfs merge=lfs -text
*.tif filter=lfs diff=lfs merge=lfs -text
*.tiff filter=lfs diff=lfs merge=lfs -text
*.mp3 filter=lfs diff=lfs merge=lfs -text
*.wav filter=lfs diff=lfs merge=lfs -text
*.mp4 filter=lfs diff=lfs merge=lfs -text
*.pdf filter=lfs diff=lfs merge=lfs -text
```

Add CAD extensions when the chapter imports native model files:
`*.sldprt`, `*.sldasm`, `*.eprt`, `*.stl`, `*.step`, and `*.stp`.

## Generated-Image Labels

Generated images must carry a label in the caption, alt text, or adjacent copy:

- `Generated concept image - not dimensional evidence`
- `Generated assembly illustration - verify against drawings`
- `Generated yearbook plate - source readiness: L2 Shop Packet, not build-ready`
- `Edited source photo - see asset ledger`

Do not use labels that imply validated/build-ready status, such as "validated
geometry", unless the row points to L3 source evidence. Do not use labels that
imply measured reality, such as "final prototype", "measured tuning", or
"as built", unless the row points to L4 empirical source evidence.

## Cross-Skill Handoff

- `idea-incubator` owns the promotion trail and `Refs #100` / `Closes #N`
  decision.
- `instrument-maker-v4` owns instrument readiness, source packet evidence, and
  the chapter contract.
- Future `instrument-showcase` should own publication layout, gallery
  navigation, and public site polish after the readiness contract is proven.
- `sheet-music` is optional and only routes in when a chapter needs notation,
  score rendering, fingering diagrams, audio renderings, or playable examples.

## Pilot Gate

Before batch rollout, the first L2+ pilot scaffold must show:

- A readiness banner that matches the source packet.
- One complete `asset-ledger.csv`.
- One complete `prompt-appendix.md` if generated imagery is used.
- LFS rules committed before large media.
- Captions or alt text labeling every generated or edited image.
- No build-ready claims unless the source packet is L3+.
- No measured/empirical claims unless the source packet is L4.
- A downstream issue or PR body using `Refs #100`.

Only after that pilot is reviewed should sibling instrument chapters be queued.
