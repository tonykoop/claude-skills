# Skill Benchmark Run Log Format

Benchmark run logs are JSON artifacts meant to be committed, attached to PRs, or
archived alongside generated outputs. They are intentionally small enough to
review in a diff.

## Required Fields

- `schema_version`: current format version, starting at `1`.
- `suite_id`: stable benchmark suite identifier.
- `skill_name` and `skill_version`: skill under test.
- `runtime_targets`: runtimes represented by the suite or case. Use this to
  keep Claude Code, Claude Desktop, Codex, Codex Desktop, and Gemini CLI
  expectations explicit even when the sample run is local.
- `runtime`: runtime or runner label, such as `codex-cli`, `claude-code`, or
  `manual-review`.
- `run_id`: stable run identifier. Use a date, PR number, or iteration label for
  archived runs.
- `created_at`: ISO-8601 timestamp or date for archived runs.
- `status`: `pass` or `fail`.
- `totals`: case and assertion counts.
- `cases`: one entry per prompt fixture, including skill name, runtime targets,
  prompt text, expected mode, expected artifacts, candidate path, watch-points,
  assertion results, and evidence.
- `archive_notes`: optional reviewer context from the suite file.

## Assertion Kinds

The lightweight harness supports deterministic artifact checks:

- `file_exists`: confirms a file or directory exists under the candidate path.
- `contains_all`: confirms all listed terms appear in a text file.
- `contains_any`: confirms at least one listed term appears in a text file.
- `not_contains_any`: confirms none of the listed terms appear in a text file.

These checks are deliberately simple. Model-in-the-loop grading can be layered on
later, but the first archive format should stay stable, readable, and easy to
reproduce without network access.
