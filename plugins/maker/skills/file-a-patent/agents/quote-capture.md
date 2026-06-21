# Quote Capture Agent

Captures inventor (and assisting-model) quotes verbatim with source provenance, then routes each quote into the correct draft section of the active invention packet.

## Trigger

Activate when the inventor says any of:
- "capture that quote"
- "record what I just said"
- "log this verbatim"
- "capture inventor quote"
- "quote capture"

## Capture Rules

1. **Never paraphrase.** Copy the text character-for-character from the source. If you cannot reproduce it exactly, say so — do not substitute a close approximation.
2. **Every quote needs a source.** Always record `source_doc` (filename, URL, or session label) and `captured_at` (ISO-8601 timestamp or reference to co-located `ip_capture` block).
3. **Label the speaker.** Use `"inventor"` for inventor words. Use `"model"` for any text the assisting model generated. Model quotes must NOT be auto-included as inventor disclosure; flag them for attorney review.
4. **Route to the correct section.** See the routing table below.

## Quote Object

```json
{
  "verbatim_quote": {
    "text": "<exact quote — no edits, no paraphrasing>",
    "speaker": "inventor",
    "source_doc": "<filename, URL, or session label>",
    "captured_at": "<ISO-8601 or 'see ip_capture block'>",
    "draft_section": "<target packet section — see routing table>",
    "attorney_flag": false
  }
}
```

Set `attorney_flag: true` when:
- `speaker` is `"model"` — model text must not be inventor disclosure without attorney review
- The quote references public disclosure, prior-art, or third-party IP
- The quote contains admission language ("I got this idea from", "I saw this in", "similar to X")

## Section Routing Table

| Quote content | Target section |
|---|---|
| Inventor describing the core idea, how it works, or what it does | `INVENTOR-QUESTIONNAIRE.md → Inventor Quotes` + `DISCLOSURE-TIMELINE.md → Inventor Quotes` |
| Inventor describing the problem being solved | `INVENTION-SUMMARY.md → Problem Solved` |
| Inventor naming prior art, background, or what they built on | `NOVELTY-CANDIDATES.md → Known Background` + `RIGHTS-PROVENANCE.md` |
| Inventor describing a first build, prototype, or test | `DISCLOSURE-TIMELINE.md → Reduction-to-Practice Events` |
| Inventor describing a demo, post, email, or public showing | `DISCLOSURE-TIMELINE.md → Public Disclosure Events` |
| Assisting-model quote (any content) | `INVENTOR-QUESTIONNAIRE.md → Assisting-Model Quotes (attorney review)` |

## Output

After capturing a quote, emit the `verbatim_quote` block inline, then:
1. State which packet section it was routed to.
2. Offer to append it to the relevant file in `_invention-packets/<slug>/`.
3. If `attorney_flag: true`, add a visible callout: `⚠ Attorney review recommended before including this in a provisional filing.`

## Model Quote Warning

Assisting-model quotes raise authorship and ownership questions for a provisional patent. The model is not an inventor. Including model-generated text as inventor disclosure without attorney review may weaken the filing. Always set `attorney_flag: true` and `speaker: "model"` for these.
