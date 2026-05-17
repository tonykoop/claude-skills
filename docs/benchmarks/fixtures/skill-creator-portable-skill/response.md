# Portable Skill Authoring Checklist

Create the skill directory with a validator-ready SKILL.md, then add a manifest.yaml entry with the canonical version, runtime, repo path, status, and last-updated fields.

Generate or hand-author agents/openai.yaml when the skill needs OpenAI/Codex metadata. Keep runtime-specific invocation syntax out of the portable skill body unless the runtime adapter owns it.

Before publishing, run quick_validate.py against the skill directory and record the command plus the "Skill is valid" result in the eval or release notes.
