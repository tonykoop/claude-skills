# Provenance Ledger Schema (`PROVENANCE-LEDGER.json`)

The provenance ledger is the skill-side counterpart to the patent-funnel dossier. It aggregates the ingestion blocks (`ip_capture`, `ip_disclosure_summary`, `verbatim_quote`) from a brainstorm session into a single machine-readable packet and cross-links it to the corresponding patent-funnel dossier issue.

## Write Path

```
_invention-packets/<slug>/PROVENANCE-LEDGER.json
```

## JSON Schema

```json
{
  "dossier_id": "<slug — matches the _invention-packets/<slug>/ folder name>",
  "created_at": "<ISO-8601 UTC — use file mtime or git commit timestamp, not model-asserted time>",
  "ip_captures": [
    {
      "utc": "<ISO-8601 UTC>",
      "local": "<ISO-8601 local with offset>",
      "timezone": "<IANA timezone>",
      "origin": "<session or clipping source>",
      "provenance_class": "soft",
      "provenance_note": "<caveat text>"
    }
  ],
  "ip_disclosure_summaries": [
    {
      "technical_field": "<field>",
      "invention_title": "<working title>",
      "problem_solved": "<problem>",
      "novel_elements": ["<element>"],
      "technical_dependencies": ["<dependency>"],
      "verbatim_inventor_quotes": [
        {
          "text": "<exact quote>",
          "speaker": "inventor",
          "source_doc": "<filename or session>",
          "captured_at": "<ISO-8601>"
        }
      ]
    }
  ],
  "quote_refs": [
    {
      "text": "<exact quote — verbatim>",
      "speaker": "inventor",
      "source_doc": "<filename or session>",
      "captured_at": "<ISO-8601>",
      "draft_section": "<target packet section>",
      "attorney_flag": false
    }
  ],
  "source_issues": [
    "<GitHub issue URL or issue ID that sourced this ingestion>"
  ],
  "key_commits": [
    "<git commit SHA — hard provenance anchors>"
  ],
  "output_folder": "<absolute path to _invention-packets/<slug>/>",
  "linked_patent_funnel_issue": "<URL or issue ID of the corresponding patent-funnel dossier issue — or null if none yet>"
}
```

## Required Fields

| Field | Type | Notes |
|---|---|---|
| `dossier_id` | string | Matches the `_invention-packets/<slug>/` folder. |
| `created_at` | string | ISO-8601 from file mtime or git commit — NOT model-asserted. |
| `ip_captures` | IpCapture[] | Zero or more `ip_capture` blocks from the session. May be empty. |
| `ip_disclosure_summaries` | IpDisclosureSummary[] | Zero or more disclosure blocks. May be empty. |
| `quote_refs` | VerbatimQuote[] | All verbatim quotes captured in the session. May be empty. |
| `source_issues` | string[] | GitHub issue URLs/IDs that triggered or sourced this ingestion. |
| `key_commits` | string[] | Git commit SHAs that serve as hard provenance anchors. |
| `output_folder` | string | Absolute path to the invention packet folder. |
| `linked_patent_funnel_issue` | string \| null | Cross-link to the corresponding patent-funnel dossier issue. Null if not yet created. |

## Integration with patent-funnel Dossiers

The provenance ledger is the **skill-side** record; the patent-funnel dossier is the **funnel-side** record. They share the same underlying facts — do NOT duplicate work; cross-link instead:

- Set `linked_patent_funnel_issue` to the funnel dossier's GitHub issue URL.
- The funnel dossier already carries: quote + source issue + key commits + output folder. The ledger reuses those fields without creating a parallel funnel.
- If no patent-funnel dossier exists yet, set `linked_patent_funnel_issue: null` and note it in `ATTORNEY-HANDOFF.md` as a TODO.

## Hard vs Soft Provenance in the Ledger

`created_at` must come from a real clock (file mtime, git commit timestamp). Use `git log --format="%cI" -1` on the packet folder's first commit if available. Do not use a model-asserted timestamp for `created_at` — this is the ledger's own anchor date and must be hard provenance. The `ip_captures[].provenance_class` entries inside the ledger may still be `"soft"` (they document what the model said); the ledger itself is anchored hard.

## Usage

After emitting an `ip_capture` and/or `ip_disclosure_summary` block during a brainstorm session:

1. Create or update `PROVENANCE-LEDGER.json` in the active `_invention-packets/<slug>/` folder.
2. Set `linked_patent_funnel_issue` if a patent-funnel dossier issue exists.
3. Append the ledger path to `ATTORNEY-HANDOFF.md` as a machine-readable evidence artifact.
4. Do not write the ledger to any public location.
