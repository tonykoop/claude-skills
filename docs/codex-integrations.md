# Codex integration map

This repo supports both Claude plugin connectors and Codex Desktop plugins.
Claude connector references live in each plugin's `CONNECTORS.md`. Codex uses a
different integration surface: installed apps, bundled plugins, local tools, and
optional MCP servers that appear as callable tools at runtime.

## Current Codex-native integrations

| Integration | Useful for | Notes |
|---|---|---|
| GitHub app | `coding` review/sprint skills; `maker` idea and build-repo handoffs | Prefer structured app calls for repo, issue, and PR metadata when available. Fall back to `gh` or local git when not. |
| Google Drive app | Maker/coding reports, build packets, sprint docs, sheets, and decks | Supports native Docs/Sheets/Slides reads, comments, batch updates, imports, exports, and file search. |
| Gmail app | Sprint summaries, vendor/fabricator mail, review requests | Prefer creating drafts unless the user explicitly asks to send. |
| Google Calendar app | Shop time, sprint ceremonies, review blocks, class scheduling | Check availability before creating events. Use exact RFC3339 times and `America/Los_Angeles` unless the user says otherwise. |
| Browser plugin | Local web QA, generated site inspection, screenshots | Use the in-app browser for localhost/file targets. Use Chrome only when the user's authenticated profile is required. |
| node_repl MCP | Quick JS transforms, package inspection, lightweight render/data checks | Use for JavaScript-native inspection without adding repo dependencies. |
| Multi-agent tools | Swarms and delegated review/exploration | Use only when the user explicitly asks for agents, delegation, or swarm work. |
| Workspace dependency runtime | Documents, spreadsheets, presentations, PDFs | Use `load_workspace_dependencies` before office-document work to locate bundled Python/Node and libraries. |

## Plugin mapping

| Plugin | Codex-only or Codex-strong integrations |
|---|---|
| `coding` | GitHub app, Gmail, Calendar, Drive, Browser/Chrome, node_repl, multi-agent |
| `maker` | Drive Docs/Sheets/Slides, Gmail, Calendar, GitHub app, Browser/Chrome, node_repl, workspace document runtimes |

## Authoring guidance

- Do not assume Claude connector registry IDs exist in Codex.
- In skill text, phrase connector usage as capability-aware: "if the app/tool is
  available, use it; otherwise generate a local artifact or handoff prompt."
- Keep hosted OAuth connectors out of plugin manifests. They require user auth
  and should remain install-time/user-choice integrations.
- Use `.mcp.json` only for local or self-hosted MCP servers with stable startup
  commands that can run on the user's machine.
- Use `.app.json` only when Codex app integration metadata is known and tested.
- Keep `CONNECTORS.md` as the human-readable source of truth for cross-runtime
  connector intent.
