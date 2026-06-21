# IP Disclosure Summary Schema (`ip_disclosure_summary`)

A concentrated disclosure block that maps directly into the correct provisional-patent sections. Emit one `ip_disclosure_summary` per invention session or brainstorm breakthrough.

## JSON Block

```json
{
  "ip_disclosure_summary": {
    "technical_field": "<one-sentence field description, e.g. 'Acoustic instrument manufacturing: slip-cast ceramic resonator bodies'>",
    "invention_title": "<working title, not the final patent title>",
    "problem_solved": "<concrete description of the problem this invention addresses>",
    "novel_elements": [
      "<element 1 — describe the structure, method, or result that appears new>",
      "<element 2>"
    ],
    "technical_dependencies": [
      "<dependency 1 — known prior art, libraries, materials, or standards this builds on>",
      "<dependency 2>"
    ],
    "verbatim_inventor_quotes": [
      {
        "text": "<exact quote, no paraphrasing>",
        "speaker": "inventor",
        "source_doc": "<filename or session description>",
        "captured_at": "<ISO-8601 timestamp or 'see ip_capture block'>"
      }
    ]
  }
}
```

## Required Fields

| Field | Type | Maps to provisional section |
|---|---|---|
| `technical_field` | string | Background — Field of the Invention |
| `invention_title` | string | Title (working draft) |
| `problem_solved` | string | Background — Description of Related Art / Problem |
| `novel_elements` | string[] | Detailed Description — Summary of the Invention |
| `technical_dependencies` | string[] | Background — Prior Art |
| `verbatim_inventor_quotes` | Quote[] | Specification notes / INVENTOR-QUESTIONNAIRE |

## Quote Object

| Field | Type | Notes |
|---|---|---|
| `text` | string | Verbatim — never paraphrase. |
| `speaker` | `"inventor"` \| `"model"` | Assisting-model quotes: use `"model"`. Flag for attorney — model quotes must NOT be included as inventor disclosure without review. |
| `source_doc` | string | Filename, URL, or session label (e.g. `Added Capabilities.md`). |
| `captured_at` | string | ISO-8601 or reference to co-located `ip_capture` block. |

## Section Mapping

```
technical_field        → Background ▶ Field of the Invention
problem_solved         → Background ▶ Description of Related Art / Problem Statement
technical_dependencies → Background ▶ Prior Art / Existing Solutions
novel_elements         → Detailed Description ▶ Summary / Preferred Embodiment
verbatim_inventor_quotes → Specification notes + INVENTOR-QUESTIONNAIRE.md
```

## Usage Notes

1. Emit `ip_disclosure_summary` after capturing the `ip_capture` block (Story #414) so both share the same session timestamp reference.
2. For each `novel_element`, use cautious phrasing: "possible point of novelty", "appears novel over known background", "attorney review needed". Do not assert patentability.
3. `technical_dependencies` prevents overclaiming — list everything this invention builds on.
4. Offer to write the block into `INVENTION-SUMMARY.md` and `DISCLOSURE-TIMELINE.md` in the active packet.
5. See `references/packet-schema.md` for the full packet-section details this block feeds into.
