# Claude Review Handoff - skills-meta

Review `skills/skills-meta` for cross-platform skill discovery, cleanup, and sync auditing across mobile, laptop, PC, Claude Code/Desktop, Codex CLI/Desktop, and Gemini CLI.

Focus on how users teach the skill all possible roots: manifest entries, `SKILLS_META_ROOTS`, repeated `--root`, exported zips, desktop install folders, repo-local copies, and unreadable mobile installs. Run `quick_validate.py`, parse YAML, run the helper in inventory/single/fix modes, and test at least one simulated extra root.

Branch from latest `main` in private repo `tonykoop/claude-skills`, commit your fixes, push your branch, and open a PR. Include validation results and a recommended sync/cleanup UX in the PR body.
