---
name: file-a-patent
version: 0.3.0
last-updated: 2026-06-20
description: Prepare private, attorney-ready invention packets and provisional-patent preparation materials from local repo evidence. Use when Codex is asked to file-a-patent, file an invention, prepare a provisional patent packet, triage patent versus trade-secret candidates, document inventorship/provenance/disclosure history, build USPTO-ready prep checklists, or assemble private IP handoff materials for inventions, musical instruments, manufacturing workflows, empirical tuning methods, AI-assisted design systems, or reverse-engineering workflows. This skill does not provide legal advice, file anything, publish anything, change licenses, or conclude that an invention is patentable.
---

# File A Patent

## Purpose

Use this skill to build private invention documentation from local evidence. The deliverable is an attorney-review packet, not a legal conclusion or a USPTO filing.

Default output location:

```text
<workspace>/_invention-packets/<repo-or-invention-slug>/
```

## Hard Guardrails

- Do not file with USPTO, Patent Center, WIPO, or any government system.
- Do not publish, push, change GitHub visibility, create releases, or modify existing `LICENSE` files.
- Do not state that something is patentable, valid, novel, non-obvious, infringing, or safe to disclose.
- Use cautious labels: "possible patent candidate", "possible trade-secret candidate", "attorney review recommended", "TODO: missing evidence".
- Prefer private local files and absolute local paths.
- Treat public disclosure risk conservatively; log evidence and uncertainty.
- If current fees, legal deadlines, or rules matter, verify against official sources first. Read `references/official-sources.md`.
- For legal decisions, recommend a registered patent attorney or agent.
- **LLM-asserted timestamps and `estimated_conception_window` dates are NOT reliable legal provenance.** Models may assert a real-time clock or fabricate precise conception dates — these claims are unreliable and must not be used as IP priority evidence. Label all model-asserted times `provenance_class: "soft"`. Real provenance = the clipping file's filesystem date + git commit timestamps. Never present a model-asserted timestamp as an authoritative conception date in any filing preparation material.

## IP Disclosure Summary

When a brainstorm session yields a breakthrough, emit an `ip_disclosure_summary` block that maps directly into provisional-patent sections:

```json
{
  "ip_disclosure_summary": {
    "technical_field": "<one-sentence field>",
    "invention_title": "<working title>",
    "problem_solved": "<concrete problem>",
    "novel_elements": ["<possible point of novelty — cautious phrasing>"],
    "technical_dependencies": ["<what this builds on>"],
    "verbatim_inventor_quotes": [
      {"text": "<exact quote>", "speaker": "inventor", "source_doc": "<doc>", "captured_at": "<ISO-8601>"}
    ]
  }
}
```

Section mapping: `technical_field` → Background (Field of Invention) · `problem_solved` → Background (Problem) · `technical_dependencies` → Background (Prior Art) · `novel_elements` → Detailed Description · `verbatim_inventor_quotes` → Specification notes + INVENTOR-QUESTIONNAIRE.

Full field spec and section-mapping table: `references/ip-disclosure-summary-schema.md`. After emitting the block, offer to write it into `INVENTION-SUMMARY.md` and `DISCLOSURE-TIMELINE.md`. Use cautious phrasing for `novel_elements` — never assert patentability.

## Core Workflow

1. **Define scope.** Identify the repo, invention slug, candidate name, and intended packet type: `provisional-prep`, `strategy-hold`, `trade-secret-review`, or `copyright-docs`.
2. **Create the packet scaffold.** Prefer `scripts/create_invention_packet.py` to copy templates into `_invention-packets/<slug>/`.
3. **Read local evidence first.** Inspect README, design docs, drawings, CAD/SCAD/SVG/PDF/DOCX/XLSX, scripts, validation data, git history, and license text. Do not rely on memory.
4. **Separate evidence classes.** Distinguish standard physics/craft background, Tony-derived empirical corrections, speculative concepts, measured reduction-to-practice, and third-party/cultural lineage.
5. **Populate packet docs.** Fill every section with evidence-backed notes, absolute file paths, and TODOs where facts are missing.
6. **Rank posture, not legal outcome.** Assign one of: possible utility patent candidate, possible design patent candidate, possible trade-secret candidate, copyright/documentation asset, hold-private, or attorney review needed.
7. **Close with missing evidence.** Summarize drawings, measurements, inventor inputs, public-disclosure facts, and prior-art searches still needed.

## Packet Files

Generate these files for serious candidates:

- `INVENTION-SUMMARY.md`
- `INVENTOR-QUESTIONNAIRE.md`
- `DISCLOSURE-TIMELINE.md`
- `RIGHTS-PROVENANCE.md`
- `PUBLIC-DISCLOSURE-RISK.md`
- `NOVELTY-CANDIDATES.md`
- `FIGURE-LIST.md`
- `EMBODIMENTS.md`
- `ATTORNEY-HANDOFF.md`
- `PROVISIONAL-PREP-CHECKLIST.md`

Use `references/packet-schema.md` when filling packet sections in detail.

## Evidence Scan Pattern

Use fast local scans before deep reading:

```bash
rg --files <repo> -g '!**/.git/**'
rg -n -i "patent|provisional|invention|novel|original|trade secret|public|license|MIT|CC BY|confidential|prototype|validation|DoE|empirical|K2|claim" <repo>
find <repo> -maxdepth 4 -type f \( -iname '*.scad' -o -iname '*.svg' -o -iname '*.dxf' -o -iname '*.stl' -o -iname '*.step' -o -iname '*.sldprt' -o -iname '*.xlsx' -o -iname '*.docx' -o -iname '*.pdf' \)
git -C <repo> log --oneline --decorate --date=short --pretty='%h %ad %s' --all --max-count=30
```

When evidence is binary, record the path and what can be inferred from filename, adjacent docs, or generated exports. Do not invent contents.

## Protection Posture Heuristics

- **Possible utility patent candidate:** new structure, method, system, manufacturing workflow, tuning/control loop, measurement method, or AI-assisted generation process that can be described as how it works.
- **Possible design patent candidate:** original ornamental shape/surface/visual configuration of an article of manufacture. Note: provisional applications cannot be filed for design inventions; verify current USPTO guidance.
- **Possible trade-secret candidate:** private empirical tables, correction factors, process recipes, ranking heuristics, prompt/workflow know-how, or unreleased datasets whose value depends on secrecy.
- **Copyright/documentation asset:** prose, drawings, templates, code, photos, spreadsheets, and packets where the value is expression or workflow documentation rather than a protectable invention.
- **Hold-private:** any candidate with uncertain disclosure history, employer overlap, collaborator uncertainty, or unclear patent/trade-secret strategy.

## Tony Repo Nuance

Read `references/tony-repo-nuance.md` for Tony-specific handling of:

- `instrument-maker` as strategy hold
- `ceramic-hang` and `wooden-hang`
- `ceramic-electric-violin`
- slip-cast ceramic instrument repos
- `reverse-engineering`

## Official Sources

Read `references/official-sources.md` before writing anything that depends on current USPTO rules, fees, or public-disclosure timing. Keep sourced statements short and link official pages in `ATTORNEY-HANDOFF.md`.

## Example Prompts

- `Use $file-a-patent to build an attorney-ready packet for /mnt/c/Users/Tony/Documents/GitHub/ceramic-hang. Output under /mnt/c/Users/Tony/Documents/GitHub/_invention-packets/ceramic-hang.`
- `Use $file-a-patent to triage /mnt/c/Users/Tony/Documents/GitHub/instrument-maker as strategy hold. Focus on trade-secret leakage risk and attorney-review questions.`
- `Use $file-a-patent to assemble a provisional-prep packet for /mnt/c/Users/Tony/Documents/GitHub/wooden-hang. Do not publish or change licenses.`
- `Use $file-a-patent to document a possible workflow invention in /mnt/c/Users/Tony/Documents/GitHub/reverse-engineering. Treat it as early-stage and avoid overclaiming.`
