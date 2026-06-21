# Packet Schema

Use this reference to populate `_invention-packets/<slug>/`.

## INVENTION-SUMMARY.md

Capture:

- Candidate name and repo path
- One-paragraph plain-English summary
- Problem solved
- Current best embodiment
- Alternate embodiments
- What is standard background
- What appears Tony-derived or unusual
- Build/reduction-to-practice status
- Key evidence paths
- Missing evidence

If an `ip_disclosure_summary` block was captured during a brainstorm session, map its fields here:

- `technical_field` → Field of the Invention subsection
- `invention_title` → working title header
- `problem_solved` → Problem Statement subsection
- `novel_elements[]` → Summary of the Invention (label each: "possible point of novelty for attorney review")
- `technical_dependencies[]` → Background / Prior Art subsection

Avoid:

- "This is patentable"
- "This is novel"
- Unsupported inventorship statements

## INVENTOR-QUESTIONNAIRE.md

Ask for:

- Legal names and residences of possible inventors
- Who conceived each feature
- Who reduced each feature to practice
- Employer/client involvement
- Contractor/friend/agent involvement
- Dates and supporting artifacts
- Confidentiality status of disclosures

Mark inventorship as attorney review, never settled.

### Inventor Quotes

Include a `## Inventor Quotes` subsection populated by the quote-capture agent (`agents/quote-capture.md`). Each entry must be verbatim — no paraphrasing. Format:

```
## Inventor Quotes

| # | Quote (verbatim) | Speaker | Source doc | Captured at | Attorney flag |
|---|---|---|---|---|---|
| 1 | "exact text" | inventor | filename.md | 2026-06-20T14:32:00Z | false |
```

Model-generated quotes go in a separate `## Assisting-Model Quotes (attorney review)` subsection with `attorney_flag: true`. These must NOT be included as inventor disclosure without attorney review.

## DISCLOSURE-TIMELINE.md

Log:

- Repository creation dates if locally or remotely available
- Private/public visibility evidence
- Demos, posts, screenshots, emails, sales, offers for sale, gifts, conference/showing events
- Who received access and whether under confidentiality
- Any AI/tool/service upload that may matter

Use absolute dates. Avoid relative terms like "recently" without a date.

If an `ip_capture` or `ip_disclosure_summary` block was captured in a brainstorm session, append it here under a `## Brainstorm Session Captures` subsection. Label model-asserted timestamps as `provenance_class: soft`. Verbatim inventor quotes from `verbatim_inventor_quotes[]` belong in the `## Inventor Quotes` subsection alongside their `source_doc` and `captured_at` fields.

### Inventor Quotes

Include a `## Inventor Quotes` subsection with verbatim quotes routed here by the quote-capture agent. Each quote carries `source_doc`, `captured_at`, and `speaker`. See `agents/quote-capture.md` for the routing table and capture rules. Never paraphrase quoted text.

## RIGHTS-PROVENANCE.md

Separate:

- Tony-created content
- Third-party references
- Traditional/cultural lineage
- Employer/client/proprietary overlap
- Open-source dependencies
- AI-generated content and prompts, if relevant
- License status and mismatch signals

Do not change license files.

## PUBLIC-DISCLOSURE-RISK.md

Classify:

- No known public disclosure from local evidence
- Possible disclosure, facts incomplete
- Known public disclosure
- Known public use/sale/offer

For each risk, include evidence path and attorney question.

## NOVELTY-CANDIDATES.md

Use cautious phrasing:

- "Possible point of novelty for attorney review"
- "Known craft background"
- "Unvalidated hypothesis"
- "Empirical know-how"
- "Potentially ornamental design feature"

Create a comparison table:

```text
candidate feature | evidence | why it might matter | known background | missing prior-art checks | posture
```

## FIGURE-LIST.md

Build a numbered figure plan:

```text
Fig. 1 - System overview
Fig. 2 - Exploded assembly
Fig. 3 - Cross-section through critical interface
Fig. 4 - Method/process flow
Fig. 5 - Alternate embodiment
Fig. 6 - Validation/test setup
```

For each figure:

- Source artifact path
- Figure purpose
- Part labels needed
- Whether it is ready, needs redrawing, or is missing

## EMBODIMENTS.md

Document:

- Preferred embodiment
- Variants by material
- Variants by manufacturing route
- Variants by scale/family member
- Variants by tuning/control method
- Failure-sensitive interfaces
- Experimental boundary conditions

## ATTORNEY-HANDOFF.md

Summarize:

- Why this packet exists
- Candidate protection paths
- Top attorney questions
- Disclosure timeline summary
- Inventorship uncertainty
- Employer/provenance issues
- Public-source links consulted
- Missing artifacts before filing

## PROVISIONAL-PREP-CHECKLIST.md

Checklist:

- Written description complete enough for preferred and alternate embodiments
- Necessary drawings listed and available
- Inventor list drafted, not finalized
- Public-disclosure timeline complete
- Prior-art search log started
- Best mode/preferred build documented
- Experimental data identified
- Attorney review queued
- Current USPTO fees/rules verified
- Decision made: file provisional, hold as trade secret, file design application, publish later, or no action
