# Archive Recovery & Repo Scaffolding

Tooling to recover scattered maker archives (CAD, code, photos, docs, media)
and scaffold them into well-structured repositories with full provenance.

---

## Concepts

### ArchiveItem

The canonical record for a single recovered file.

```python
class ArchiveItem:
    path: str               # forward-slash path (in-memory, no disk access)
    kind: FileKind          # cad | photo | doc | code | media | unknown
    inferred_project: str   # guessed from path heuristics
    content_hash: str       # SHA-256 of file bytes (or stub from path)
    mtime: float            # Unix timestamp
    size_bytes: int

    # Provenance flags — always check these
    kind_is_inferred: bool          # False = extension-lookup fact
    project_is_inferred: bool       # True = always heuristic in v1
    provenance_note: str            # human-readable explanation
```

### FileKind

| Value     | Typical extensions                                    |
|-----------|-------------------------------------------------------|
| `cad`     | `.step`, `.stl`, `.f3d`, `.dxf`, `.kicad_pcb`, …     |
| `photo`   | `.jpg`, `.png`, `.raw`, `.cr2`, `.heic`, …            |
| `doc`     | `.pdf`, `.md`, `.csv`, `.yaml`, `.xlsx`, …            |
| `code`    | `.py`, `.ino`, `.cpp`, `.rs`, `.sh`, …                |
| `media`   | `.mp4`, `.mov`, `.wav`, `.flac`, …                    |
| `unknown` | no rule matched                                       |

---

## Workflow

```
FileRecord list           classify_archive()          group by project
(in-memory paths)    ──►  list[ArchiveItem]    ──►   dict[project, items]
                                                           │
                                              plan_scaffold(project, items)
                                                           │
                                                     ScaffoldPlan
                                                   (dirs, LFS rules, ledger)
```

### Step 1 — Build FileRecords

No filesystem access is required. Supply whatever metadata you have:

```python
from archive_recovery import FileRecord

records = [
    FileRecord(path="synth_v3/firmware.ino", size_bytes=4096, mtime=1700000000.0),
    FileRecord(path="synth_v3/case.step",    size_bytes=210_000_000),  # large binary
    FileRecord(path="synth_v3/build01.jpg"),
]
```

### Step 2 — Classify

```python
from archive_recovery import classify_archive

items = classify_archive(records)
for item in items:
    print(item.kind, item.inferred_project, item.kind_is_inferred)
# cad   synth_v3  False   ← extension fact
# photo synth_v3  False
```

### Step 3 — Group by project

```python
from collections import defaultdict

by_project: dict[str, list] = defaultdict(list)
for item in items:
    by_project[item.inferred_project].append(item)
```

### Step 4 — Plan the scaffold

```python
from archive_recovery import plan_scaffold

plan = plan_scaffold("synth_v3", by_project["synth_v3"])

print(plan.dirs)         # [ScaffoldedDir(path='cad', ...), ...]
print(plan.lfs_rules)    # [LFSRule(pattern='cad/case.step', ...)]
print(plan.readme_skeleton[:200])
```

### Step 5 — Inspect the evidence ledger

```python
audit = plan.evidence_ledger.audit()
print(f"Facts: {audit['facts']}, Inferred: {audit['inferred']}")

for entry in plan.evidence_ledger.facts():
    print("FACT:", entry.claim)

for entry in plan.evidence_ledger.inferences():
    print("INFERRED:", entry.claim, f"[{entry.confidence}]")
```

### Step 6 — Export for storage

```python
import json

with open("scaffold-plan.json", "w") as f:
    json.dump(plan.export_dict(), f, indent=2)
```

---

## Evidence Ledger Discipline

Tony's provenance discipline: **every claim about a recovered artefact must be
tagged** as either a verifiable archive fact or an inference.

| Kind       | Meaning                                                    |
|------------|------------------------------------------------------------|
| `fact`     | Verifiable from the archive byte-stream (path, extension, hash, size) |
| `inferred` | Derived from heuristics (project grouping, semantic category, dates)   |

Rules:
1. Extension-to-kind mapping → **fact** (explicit lookup table).
2. No-extension / dotfile → **inferred** (code heuristic).
3. Project identity → **always inferred** in v1.
4. LFS decision (>100 MB) → **inferred** (size threshold heuristic).
5. Directory layout → **inferred** (kind-to-dir mapping).

Never promote an `inferred` entry to authoritative without human confirmation.

---

## Git LFS Rules

The scaffold planner emits a file-specific LFS pattern for every file >100 MB:

```
cad/case.step     # 210 MB  ← LFS-tracked
photos/build.jpg  # 2 MB    ← committed normally
```

After scaffold review, wire up LFS before adding large files:

```bash
git lfs install
git lfs track "cad/case.step"
# (or use the patterns from plan.lfs_rules)
git add .gitattributes
```

---

## Classifier — Extension Table

The classifier ships 80+ extension mappings covering professional CAD (STEP,
DXF, KiCad, Fusion 360, SCAD), photography (RAW, HEIC, TIFF), documents,
25+ code languages, and common audio/video formats.

All extension lookups are **archive facts** (`kind_is_inferred=False`).
Heuristic fallbacks (no extension, dotfiles) are **always flagged inferred**.

---

## Running Tests

```bash
pip install pydantic pytest
pytest tests/test_archive_recovery.py -v
```

All tests are offline — no filesystem mutation, no network access.

---

## Directory Layout

```
archive_recovery/
  __init__.py      public API surface
  models.py        ArchiveItem, FileRecord, FileKind
  classifier.py    classify_archive()
  scaffold.py      plan_scaffold(), ScaffoldPlan
  evidence.py      EvidenceLedger, EvidenceEntry
  README.md        this file
tests/
  test_archive_recovery.py
```
