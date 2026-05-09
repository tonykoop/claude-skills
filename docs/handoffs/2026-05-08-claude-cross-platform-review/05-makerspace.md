# Claude Review Handoff - makerspace

Review `skills/makerspace` as the portable snapshot of the standalone makerspace skill repo. Ensure it works as a packaged skill on Claude Code/Desktop, Codex CLI/Desktop, Gemini CLI, and mobile zip-upload workflows.

Focus on package size, legacy eval workspace placement, relative references, shop-profile assumptions, generated `agents/openai.yaml`, and whether repo-level material copied from the standalone repo should stay bundled or move behind references/assets. Run `quick_validate.py`, parse YAML/JSON, and do a 3-prompt fabrication smoke eval.

Branch from latest `main` in this repo, commit your fixes, push your branch, and open a PR. Include validation results and recommendations for keeping the standalone `makerspace` repo synchronized.
