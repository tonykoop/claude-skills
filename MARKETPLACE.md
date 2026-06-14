# tony-koop marketplace

A Claude Code plugin marketplace backed by this repo. Two plugins:

| Plugin | What it does | Skills |
|---|---|---|
| `maker` | Physical-world design and personal practice | instrument-maker, sheet-metal, maker-engineering, makerspace, laser-art, habitat-maker, reverse-engineer, sheet-music, yoga-sequencer, playlist-builder, idea-incubator, file-a-patent |
| `coding` | Engineering operations and developer tooling | tmux-sprint, sprint-supervisor, sprint-update, merge-review, run-swarm, ci-triage, scaffold-hygiene, disk-cleanup, skills-meta |

## Install (Claude Code CLI)

Add the marketplace once:

```text
/plugin marketplace add C:\Users\Tony\Documents\GitHub\claude-skills
```

You can also use a `file://` URL, or `https://github.com/tonykoop/claude-skills.git`
to pull from GitHub instead of the local checkout.

Then install whichever plugins you want:

```text
/plugin install maker@tony-koop
/plugin install coding@tony-koop
```

## Install (Codex app)

Use **Add marketplace** with:

```text
Source: https://github.com/tonykoop/claude-skills.git
Git ref: main
Sparse paths:
.claude-plugin
.codex-plugin
plugins/coding
plugins/maker
```

The `.claude-plugin` path is required by the marketplace loader. The
`.codex-plugin` path keeps the Codex-specific marketplace metadata available
too. Without these root manifest directories, Codex stages only the plugin
folders and the marketplace root is missing a supported manifest.

Codex-specific app/tool mappings are documented in
[`docs/codex-integrations.md`](docs/codex-integrations.md).

## Auto-update

Open the `/plugin` panel, find `tony-koop`, toggle **Auto-update** on. From
then on, every change pushed to `main` flows in next session with a
`/reload-plugins` prompt.

For managed/org-wide rollout, add to `~/.claude/managed-settings.json`:

```json
{
  "extraKnownMarketplaces": [
    {
      "name": "tony-koop",
      "source": "https://github.com/tonykoop/claude-skills.git",
      "autoUpdate": true
    }
  ]
}
```

## Versioning workflow

Each plugin has its own semver in `plugins/<plugin>/.claude-plugin/plugin.json`.
When you change a skill inside a plugin:

1. Bump the affected skill's `version` (in its `SKILL.md` or `manifest.yaml` entry).
2. Bump the *plugin's* `version` in `plugins/<plugin>/.claude-plugin/plugin.json`.
3. Commit, push. Users on auto-update see it on next session.

Reserve a major bump (e.g. `1.0.0` -> `2.0.0`) for breaking changes: skill
renames, removed skills, restructured plugin contents.

## Repo layout

```
claude-skills/
|-- .claude-plugin/
|   `-- marketplace.json
|-- .codex-plugin/
|   `-- marketplace.json
|-- plugins/
|   |-- maker/
|   |   |-- .claude-plugin/plugin.json
|   |   |-- .codex-plugin/plugin.json
|   |   `-- skills/
|   |       |-- instrument-maker/
|   |       |-- sheet-metal/
|   |       `-- ... (12 skills)
|   `-- coding/
|       |-- .claude-plugin/plugin.json
|       |-- .codex-plugin/plugin.json
|       `-- skills/
|           |-- tmux-sprint/
|           |-- skills-meta/
|           `-- ... (9 skills)
|-- claude/               # Claude-specific commands/hooks (not in any plugin yet)
|-- codex/                # Codex CLI skills (consumed directly by Codex)
|-- docs/
|-- manifest.yaml         # canonical version registry (still authoritative for SKILL versions)
`-- scripts/
```

## Cowork mode note

Cowork's Anthropic-bundled skills (docx, xlsx, pptx, pdf, etc.) live in a
separate session-scoped folder Cowork manages. This marketplace doesn't
touch those.
