# tony-koop marketplace

This repo is a Claude Code plugin marketplace. It hosts four plugins, each
bundling a related set of skills. Install once; updates flow in via `git pull`.

## Plugins

| Plugin | What's inside | Audience |
|---|---|---|
| `heifer-zephyr-maker` | instrument-maker, maker-engineering, makerspace, sheet-metal, laser-art, habitat-maker, reverse-engineer, sheet-music | The Heifer Zephyr maker brand — anyone designing instruments, jigs, or wildlife habitat |
| `tony-life` | yoga-sequencer, playlist-builder, idea-incubator | Personal-practice tools |
| `tony-eng-ops` | tmux-sprint, merge-review, sprint-supervisor, sprint-update, run-swarm, ci-triage, scaffold-hygiene, disk-cleanup | WRFCoin / internal engineering operations |
| `skills-meta` | skills-meta | Drift-audit tool for skill installs across runtimes |

## Install (Claude Code CLI)

Add this marketplace once:

```text
/plugin marketplace add C:\Users\Tony\Documents\GitHub\claude-skills
```

You can use a `file://` URL, the absolute Windows path, or
`https://github.com/tonykoop/claude-skills.git` if you'd rather pull from
GitHub than your local checkout.

Then install whichever plugins you want:

```text
/plugin install heifer-zephyr-maker@tony-koop
/plugin install tony-life@tony-koop
/plugin install tony-eng-ops@tony-koop
/plugin install skills-meta@tony-koop
```

## Auto-update

In Claude Code, open the `/plugin` panel, find the `tony-koop` marketplace,
and toggle **Auto-update**. When the toggle is on, Claude Code re-fetches the
marketplace on each session and prompts you to reload plugins after every
upstream change.

To enable auto-update org-wide via managed settings, drop this into
`~/.claude/managed-settings.json` (or the platform equivalent):

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

Each plugin tracks its own semver in `plugins/<plugin>/.claude-plugin/plugin.json`.
When you change a skill inside a plugin:

1. Bump the affected skill's `version` in its `SKILL.md` (or the per-skill
   entry in `manifest.yaml`).
2. Bump the **plugin's** `version` in `plugins/<plugin>/.claude-plugin/plugin.json`.
3. Commit, push. Users with auto-update on see the update on next session.

Reserve a major bump (e.g. `1.0.0 -> 2.0.0`) for breaking changes —
skill renames, removed skills, or restructured plugin contents.

## Cowork mode note

Cowork's Anthropic-bundled skills (docx, xlsx, pptx, pdf, canvas-design,
consolidate-memory, schedule, setup-cowork, skill-creator, web-artifacts-builder,
yoga-playlist-builder) live in a separate session-scoped folder Cowork manages
itself. This marketplace doesn't touch them.

## Repo layout

```
claude-skills/
├── .claude-plugin/
│   └── marketplace.json
├── plugins/
│   ├── heifer-zephyr-maker/
│   │   ├── .claude-plugin/plugin.json
│   │   └── skills/
│   │       ├── instrument-maker/
│   │       └── ...
│   ├── tony-life/...
│   ├── tony-eng-ops/...
│   └── skills-meta/...
├── claude/                  # Claude-specific commands/hooks (not in any plugin yet)
├── codex/                   # Codex CLI skills (consumed directly by Codex)
├── docs/
├── manifest.yaml            # canonical version registry — still authoritative for SKILL versions
└── scripts/
    └── migrate-to-marketplace.ps1   # one-shot reorg
```
