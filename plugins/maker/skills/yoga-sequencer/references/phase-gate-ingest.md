# Phase-Gate Class Ingest

Use this reference when preparing yoga class captures for Rosetta training. The public ingest layer defines the class JSON shape, four-array parse target, and go/no-go phase gates. Private class audio, transcripts, and corpus files stay outside this repo.

## Input Class Shape

Each source class is a JSON object:

```json
{
  "class_id": "class-YYYY-MM-DD-slug",
  "teacher": "Tony",
  "duration_min": 60,
  "source": "private-corpus-id-or-local-capture",
  "segments": [
    {
      "start_sec": 0,
      "end_sec": 60,
      "kind": "audio",
      "text": "Opening breath bed",
      "pacing": "slow"
    },
    {
      "start_sec": 60,
      "end_sec": 120,
      "kind": "choreography",
      "shorthand": "DD // 5B",
      "text": "Down dog hold"
    },
    {
      "start_sec": 120,
      "end_sec": 150,
      "kind": "theme",
      "text": "Notice the space between effort and ease."
    }
  ]
}
```

## Four-Array Parse Target

The parser produces:

- `metadata`: class id, teacher, duration, source, and segment count
- `audio_timeline`: timed audio/pacing segments
- `choreography_raw`: shorthand segments plus parsed token labels
- `thematic_drops`: timed theme/intention segments and detected theme terms

## Phase Gates

- `anchor`: exactly 1 class; proves one file parses end to end
- `triangulation`: at least 3 classes; checks the parser generalizes beyond the anchor
- `micro_batch`: 3 to 5 classes; checks batch behavior before scale
- `bulk`: at least 35 classes; full-corpus pass

Every phase fails closed if any class has malformed timing, no segments, or missing `metadata`, `audio_timeline`, `choreography_raw`, or `thematic_drops` arrays. A failed gate should be fixed before moving to the next phase.
