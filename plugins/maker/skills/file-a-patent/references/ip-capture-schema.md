# IP Capture Schema (`ip_capture`)

Emit an `ip_capture` block whenever the inventor uses a trigger phrase such as:

- "capture IP timestamp"
- "log this as IP"
- "timestamp this invention"
- "record IP moment"

## JSON Block

```json
{
  "ip_capture": {
    "utc": "<ISO-8601 UTC datetime, e.g. 2026-06-20T14:32:00Z>",
    "local": "<ISO-8601 local datetime with offset, e.g. 2026-06-20T07:32:00-07:00>",
    "timezone": "<IANA timezone name, e.g. America/Los_Angeles>",
    "origin": "<brief description of the session or clipping source, e.g. 'Gemini brainstorm session, Added Capabilities.md'>",
    "provenance_class": "soft",
    "provenance_note": "Model-asserted times are NOT reliable legal provenance. Real provenance = the clipping file date + git commit timestamps. This block is a soft conception marker only."
  }
}
```

## Required Fields

| Field | Type | Description |
|---|---|---|
| `utc` | string | ISO-8601 UTC timestamp. If the model does not have a reliable system clock, use the session date from the clipping source; flag uncertainty in `provenance_note`. |
| `local` | string | ISO-8601 local timestamp with UTC offset. |
| `timezone` | string | IANA timezone string. |
| `origin` | string | Short description of the source session or clipping. |
| `provenance_class` | `"soft"` | **Always `"soft"` for model-asserted times.** Hard provenance requires a real clock (file mtime, git commit, notary). |
| `provenance_note` | string | Human-readable caveat. Never omit. |

## Provenance Classes

| Class | Source | Legal weight |
|---|---|---|
| `"soft"` | Model-asserted, session-inferred | Low — soft conception marker only |
| `"hard"` | File mtime, git commit SHA + timestamp, notarized record | High — use as primary evidence |

The `ip_capture` block always uses `"soft"`. Hard provenance comes from the clipping file's filesystem date and the git commit log. See the guardrail in SKILL.md and Story #418.

## Usage

Emit the block inline in the conversation response, then offer to append it to `DISCLOSURE-TIMELINE.md` inside the active invention packet. Do not assert that the timestamp is legally authoritative.
