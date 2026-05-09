# Claude Review Handoff - maker-engineering

Review `skills/maker-engineering` for cross-platform compatibility and routing correctness across Claude Code/Desktop, Codex CLI/Desktop, Gemini CLI, and mobile zip uploads.

Focus on umbrella-vs-specialist boundaries, portable specialist names, references packaging, trigger specificity, and whether it can route when the target specialist is installed in another repo or runtime. Run `quick_validate.py`, parse YAML, and do a 3-prompt routing smoke eval.

Branch from latest `main` in this repo, commit your fixes, push your branch, and open a PR. Include validation results and any cross-runtime routing caveats in the PR body.
