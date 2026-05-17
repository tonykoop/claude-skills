# Claude Review Handoff - reverse-engineer

Review `skills/reverse-engineer` as the portable snapshot of `reverse-engineering/skills/v1/reverse-engineer`. Ensure it works across Claude Code/Desktop, Codex CLI/Desktop, Gemini CLI, and mobile zip-upload workflows.

Focus on uncertainty language, image/photo handling without platform-specific tools, builder-handoff boundaries, references packaging, and possible trigger overlap with the broader `reverse-engineering` repo skill. Run `quick_validate.py`, parse YAML, and do a 3-prompt reverse-engineering smoke eval.

Branch from latest `main` in this repo, commit your fixes, push your branch, and open a PR. Include validation results and any recommended synchronization approach for the standalone reverse-engineering repo.
