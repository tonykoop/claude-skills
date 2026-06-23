# Changelog

## 0.3.0 - 2026-06-20

- `references/ip-capture-schema.md` — ISO-8601 `ip_capture` JSON block schema;
  `provenance_class` always `"soft"` for model-asserted times; provenance-class
  table; trigger phrases (Story #414).
- `references/ip-disclosure-summary-schema.md` — concentrated disclosure block
  (`technical_field`, `invention_title`, `problem_solved`, `novel_elements[]`,
  `technical_dependencies[]`, `verbatim_inventor_quotes[]`) with section-mapping
  table into provisional-patent sections (Story #415).
- `agents/quote-capture.md` — verbatim quote capture agent; no-paraphrase rule;
  section routing table; `attorney_flag` rules for model-generated quotes
  (Story #416).
- `references/provenance-ledger-schema.md` — `PROVENANCE-LEDGER.json` schema
  wiring `ip_captures`, `ip_disclosure_summaries`, and `quote_refs` to the
  patent-funnel dossier; `linked_patent_funnel_issue` cross-link field;
  `created_at` must be hard provenance (Story #417).
- SKILL.md Hard Guardrails — LLM-asserted timestamps and
  `estimated_conception_window` dates are soft provenance only; real provenance
  = clipping file mtime + git commit SHA; added IP Capture, IP Disclosure
  Summary, Verbatim Quote Capture, and Provenance Ledger workflow sections
  (Stories #414–#418).
- `evals/evals.json` — added eval #6 `llm-timestamp-soft-provenance-guardrail`.
- Bumps SKILL.md to v0.3.0.

## 0.2.0 - 2026-06-19

- `evals/evals.json` — 5 machine-runnable evals: hard-guardrails-no-filing-or-publishing,
  cautious-labels-no-patentability-conclusion, local-evidence-first-no-memory-fabrication,
  separate-evidence-classes-no-overclaiming, missing-evidence-summary-required.
- Bumps SKILL.md to v0.2.0.

## 0.1.0 - 2026-05-25

- Imported `file-a-patent` into the Maker plugin.
- Kept the private invention packet workflow, USPTO/source-reference
  guardrails, attorney-review packet templates, OpenAI agent metadata, and
  `create_invention_packet.py` scaffold script.
- Excluded standalone repository internals and generated zip artifacts from the
  plugin package.
