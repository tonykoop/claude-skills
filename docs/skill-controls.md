# Skill Controls

Skill controls are the rules and tools that prevent a growing skill ecosystem
from becoming a pile of prompt fragments.

## Control Surfaces

- Activation: precise frontmatter descriptions and trigger phrases.
- Routing: umbrella skills route; specialist skills do the work.
- Versioning: every skill has structured version metadata.
- Packaging: zips are built from tagged commits.
- Drift detection: installed versions are checked against `manifest.yaml`.
- Deprecation: old skills remain documented until removed from every device.
- Benchmarking: fragile skills get repeatable test prompts and watch-points.

## Runtime Targets

Preferred runtime support includes:

- Claude Desktop and Claude Code;
- Codex and Codex Desktop;
- Gemini CLI;
- future plugins, connectors, routines, hooks, and automations.

Runtime-specific implementation details should live under `claude/`, `codex/`,
or `gemini/`. Portable skill logic should live under `skills/`.

## Public Release Gate

Before public release, each skill should be reviewed for:

- personal paths and secrets;
- WRFCoin-only assumptions that need project-neutral wording;
- private repo names or operational details that should be generalized;
- bundled resources that are missing from the repo;
- deterministic setup instructions;
- benchmark or smoke-test coverage.

