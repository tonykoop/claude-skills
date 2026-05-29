# Private Media Decision Stub

Use this compact owner checklist before promoting photo albums, family
archives, scanned albums, personal video, or imagegen-assisted private-media
ideas into downstream repo work.

The goal is to capture the decisions that make a pilot safe to scaffold. If an
answer is unknown, keep it as an explicit blocker. Do not fill gaps with
shareable-by-default assumptions, and do not start repo scaffolding,
imagegen/layout studies, media import, or print/export work until the blocking
answers are recorded.

## Copy-Pasteable Decision Stub

```markdown
## Private Media Pilot Decisions

Source issue(s): #<N>, #<sibling-or-duplicate-if-any>

### Pilot batch

- One batch to pilot: <album/folder/event/date range/export/scanned envelope>
- Source location: <external drive/cloud export/archive path/unknown>
- Broad archive import requested? no / yes, blocked until pilot review

### Repo and access

- Target repo name: <name or unknown>
- Visibility: private / unknown
- Allowed collaborators: <names or unknown>
- Sharing/export rule: private proof only / family review / vendor print /
  unknown

### Reviewers and off-limits boundary

- Privacy reviewer: <name or unknown>
- Family reviewer: <name / not needed / unknown>
- Proof reviewer: <name or unknown>
- Off-limits people/faces/minors: <list or unknown>
- Off-limits homes/schools/events/locations/date ranges: <list or unknown>
- Sensitive documents or captions to exclude: <list or unknown>

### Source-photo policy

- Original policy: external-ledger-only / lfs-original / derived-only /
  exclude / unknown
- LFS ready before import: yes / no, blocker
- Raw-import folders blocked by `.gitignore`: yes / no, blocker
- Originals kept out of `exports/` and public examples: yes / no, blocker

### Metadata and provenance

- EXIF/GPS rule: strip-derived / quarantine-originals / preserve-private /
  unknown
- Source ledger planned: yes / no, blocker
- Evidence ledger planned: yes / no, blocker
- Captions/memories kept separate from observed file facts: yes / no, blocker

### Imagegen and layout boundary

- Allowed imagegen uses: layout concept / cover concept / restoration study /
  collage concept / caption tone / proof-review prompt / none / unknown
- Generated or heavily transformed outputs labeled
  `not a documentary original`: yes / no, blocker
- Prompts avoid full names, addresses, school names, exact locations,
  sensitive dates, and uncleared faces: yes / no, blocker

### Proof/export gate

- First proof target: internal PDF / family review proof / vendor print test /
  no export yet / unknown
- Watermarked proof required before sharing/export: yes / no, blocker
- `reviews/proof-signoff.md` required before vendor upload, family share,
  public preview, or print-ready export: yes / no, blocker
```

## Route After The Stub

- If pilot batch, visibility, reviewers, source-photo policy, metadata policy,
  LFS readiness, and proof/export rule are all answered, draft the downstream
  scaffold issue using `Refs #N`.
- If one or more answers are unknown, keep the promotion in `defer` or
  `comment` state and ask only for the missing decisions.
- If sibling captures describe the same private-media project, preserve each
  source as a `Refs` anchor until the owner confirms duplicate handling.
- If the idea is really a public design-book, portfolio, or generic visual
  concept without private source media, route out of the private-media pilot
  workflow.
