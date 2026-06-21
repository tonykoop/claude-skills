# Gemini Notebooks / NotebookLM Grounding

Design doc for Story #411 (Epic #406). Defines how clips sourced from **Google
NotebookLM** (also marketed under Gemini as "Gemini Notebooks") enter the idea
pipeline and the extra scrutiny they need before being trusted as issue content.

---

## What grounding means in this context

NotebookLM lets you pin up to ~600 source documents ("Sources") to a notebook
and chat with the AI with those documents as grounding context. The chat
transcript that exits NotebookLM (via "Export chat" or copy-paste) may therefore
contain:

- Verbatim text quoted from sources the AI retrieved
- AI-synthesized summaries whose provenance is the source set, not the user's
  direct thinking
- The user's own prompts and reactions, which *are* genuine captured ideas

**Why this matters for the pipeline:** the dedup fingerprint is keyed on
`conversation_id + idea block text`. If grounded quotes land in the inbox as
"ideas", they will generate issues that are actually borrowed from third-party
sources — a quality problem. The pipeline must tag these clips specially and
route them to human review before filing.

---

## Front-matter extension

Inbox files whose content came from a NotebookLM session MUST carry an extra
front-matter key:

```yaml
---
source: gemini
gemini_variant: notebooklm
notebook_id: <stable notebook URL hash or human name, if available>
conversation_id: <sha256 of transcript>
exported_at: <ISO-8601 UTC>
title: <brainstorm title>
---
```

The `gemini_variant: notebooklm` flag is the routing signal. All stages that
consume inbox files SHOULD inspect this key:

- `inbox_watcher.py`: detect `gemini_variant` via a front-matter scan and attach
  it to the dispatch payload
- `gemini_to_github.py`: label issues `needs-clarification` (in addition to
  `capture`) when `gemini_variant == notebooklm`

### Front-matter detection snippet

```python
import re

_FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_NOTEBOOKLM_RE = re.compile(r"gemini_variant\s*:\s*notebooklm", re.IGNORECASE)

def is_notebooklm_clip(content: str) -> bool:
    m = _FM_RE.match(content)
    if not m:
        return False
    return bool(_NOTEBOOKLM_RE.search(m.group(1)))
```

---

## Limitations (read before relying on this)

The following claims about NotebookLM are **unconfirmed** as of 2026-06 and
MUST be manually verified before treating them as reliable pipeline inputs:

| Claim | Risk if wrong | Mitigation |
|---|---|---|
| Up to ~600 sources per notebook | Actual limit may be lower; export quality degrades at scale | Treat large-source notebooks as degraded; route to `needs-clarification` |
| Notebook sync is stable across sessions | The notebook may resync and alter "stored" facts between export runs | Always re-export from source; never rely on a cached export |
| "Export chat" produces a complete fidelity transcript | May omit early turns or truncate long responses | Verify transcript length against session view before ingesting |
| NotebookLM session IDs are stable across page refreshes | IDs may be transient, breaking the dedup anchor | Derive `conversation_id` from `sha256(transcript)`, not URL |

### Recommended operating posture

1. Always label NotebookLM-derived issues `needs-clarification`.
2. Do not auto-merge NotebookLM clips into the main backlog without a human
   reading the `## Capture` block and confirming the idea originated from the
   user (not quoted source material).
3. If the notebook contains external research sources, scan the idea block for
   quoted text (e.g. longer verbatim paragraphs, citation markers) and strip or
   note them in the issue body.
4. Until NotebookLM export fidelity is confirmed stable, treat each clip as a
   *draft* rather than a finalized idea.

---

## Stage 1b — NotebookLM source variant

The standard Stage 1 of the pipeline (see
[gemini-export-pipeline.md](gemini-export-pipeline.md)) handles direct Gemini
chat exports. Stage 1b covers NotebookLM as an alternative intake path:

```
[1b] NotebookLM chat / "Export chat"
       | manual export (no stable API as of 2026-06)
       v
[2]  Obsidian vault inbox  (vault/00-inbox/*.md)
       | front-matter must include gemini_variant: notebooklm
       v
[3]  Claude parse  (Intake mode + prior-lessons pre-read)
       | identical to standard path, EXCEPT:
       | — label includes needs-clarification
       | — issue body notes the NotebookLM origin
       v
[4]  GitHub issues  (human review required before closing needs-clarification)
```

There is currently no NotebookLM export API; all exports are manual. Do not
design automation that assumes a programmatic export path until one is confirmed.

---

## Trigger phrases added to SKILL.md

The following phrases route to NotebookLM-aware Intake mode:

- `gemini notebooks`
- `notebooklm grounding`
- `notebook clip`
- `clip from notebook`

---

## See also

- [gemini-export-pipeline.md](gemini-export-pipeline.md) — main pipeline design
- [domain-label-routing.md](domain-label-routing.md) — label routing table
