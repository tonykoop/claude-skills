# Techniques Catalog — Data Model & Capture Flow

The techniques catalog records *demonstrations of how to make things* by real
makers, with deep-links to the exact moment the technique is shown. It is the
"HOW, by people" companion to the bibliography's "what knowledge."

## Entry schema (`references/techniques.yaml`)

| field | meaning |
|---|---|
| `key` | stable hand-writable id (never rename once cited) |
| `technique` | the thing being demonstrated |
| `creator` | the maker/person |
| `platform` | `youtube` / `maker-tok` / `instagram` / `wikihow` / `makerspace` / `web` |
| `url` | live pointer (disposable — may rot) |
| `start` | seconds into a video; **only when `status: confirmed`** |
| `capture` | path to a local Obsidian clip, e.g. `captures/<key>.md` (durable) |
| `grounds` | list of bibliography `registry.yaml` keys this technique rests on |
| `instruments` | instrument/family tags (shared vocab with instrument-tagging.md) |
| `tags` | freeform technique tags (laser, glue-up, reed-scraping, ...) |
| `status` | `confirmed` or `unconfirmed` |
| `what_they_show` | durable plain-language description; survives link death |

## Capture flow with Obsidian Web Clipper

1. While watching/reading, clip the page with the Obsidian Web Clipper. It saves
   markdown + images locally to your vault, and writes Properties as YAML
   frontmatter — so the clip can carry `creator`, `url`, `platform`, etc.
2. For a video, note the moment: on YouTube use Share → "Start at" (or append
   `&t=NNs`) to read the seconds value; put that integer in `start`.
3. Write `what_they_show` in your own words from what you actually saw. This is
   the durable record — the live link is just a pointer to it.
4. Set `status: confirmed`. The entry is now citable.

Point `capture:` at the clipped note (e.g. `captures/schama-layered-relief.md`)
so the registry and the local clip stay linked. If the URL later dies, the
capture still holds the technique.

## Why the two-status model is non-negotiable

An agent can discover that a maker exists and find their channel. An agent
*cannot* watch a video and confirm a technique appears at second 116. So:

- Agents may add `unconfirmed` seeds: real `creator` + real `url`, blank `start`,
  honest "UNVERIFIED SEED" note. Useful head start, no fabrication.
- Only a human who watched promotes to `confirmed` with a real timestamp.
- `gen_techniques.py check` refuses to let a repo cite an `unconfirmed` entry.

A confabulated timestamp is worse than a missing one: the first wrong jump-link
a reader clicks discredits every other citation in the repo.

## Rendering to Quarto (desktop)

```bash
python3 scripts/gen_techniques.py site techniques-catalog.qmd
quarto render techniques-catalog.qmd
```

Confirmed YouTube demos render with Quarto's verified video shortcode at the
exact moment:

```
{{< video https://www.youtube.com/watch?v=VIDEOID start="116" >}}
```

(The `start` value is in seconds; the shortcode also accepts youtu.be and
/embed/ URL forms.) Non-video platforms render as links. Unconfirmed seeds are
listed in a separate "not citable" section so the catalog is honest about what
has and hasn't been verified.

## Per-repo citation (`.techniques.yaml`)

```yaml
instrument: Laser Mandala Clock
repo: laser-mandala-clock
cites:
  - key: <confirmed-technique-key>
    why: <one specific sentence on how this demo shaped this build>
```

Same shape as `.citations.yaml` for sources. `gen` writes `TECHNIQUES.md`
grouped as a maker-credit list with the moment timestamp shown as `m:ss`.
