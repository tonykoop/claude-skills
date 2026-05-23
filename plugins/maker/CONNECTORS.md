# Recommended connectors for the `maker` plugin

These connectors aren't required, but each one unlocks specific skills inside
the `maker` plugin. Connect any of them from Claude's connector registry
(search by name, click Connect, follow the auth flow). Skills will start
calling them automatically once they're available.

## Hosted connectors (one-click from registry)

| Connector | Pairs with | What it adds |
|---|---|---|
| **Adobe for creativity** | `laser-art`, `sheet-music`, `instrument-maker` (visual register), shop packets across all maker skills | Batch photo editing, social variations, Quick Cut sizzle reels, asset library, design-from-template (flyers/posters/packets). Tony's brand work runs through here. |
| **Wolfram** | `instrument-maker`, `sheet-metal`, `maker-engineering` (DoE) | Acoustic models, tube/pipe physics, bend-allowance and flat-pattern math, parametric design tables, mass/inertia for jigs and fixtures. The acoustic-law guard in `instrument-maker` is sharper with real Wolfram evaluation behind it. |
| **GitHub** | `idea-incubator`, `instrument-maker` (design-book chapter contract), `habitat-maker` (build packets) | Capture ideas as issues, run promotion workflows, manage build-repo READMEs, push generated packets up as PRs. |
| **Trimble SketchUp** | `instrument-maker`, `habitat-maker`, `makerspace` (jigs, fixtures, enclosures) | "Build me this model" / "iterate this scene" — quick 3D sketching when SolidWorks is too heavy. |
| **Figma** | `laser-art`, `instrument-maker` (concept register), build-packet covers | Pull design context, iterate posters/labels/cut-sheets that started on a tablet. |
| **Canva** | `laser-art`, `idea-incubator` (design-book pilots) | Alternative to Adobe for templated visuals, especially for non-print social or quick mood boards. |
| **Spotify** | `playlist-builder` | First-party playlist creation, currently-playing track context, library reads. Required for the SoundCloud → Spotify mirror flow. |
| **Lumin** | `makerspace`, `sheet-metal` (shop packets), `instrument-maker` (capstone deck handoffs) | Markdown → PDF for signed-off build packets, signature requests when shop work needs sign-off (Maker Nexus checkouts, fabricator handoffs). |
| **Autodesk Product Help** | `sheet-metal`, `makerspace`, `instrument-maker` (Fusion side workflows) | Searchable Autodesk docs — useful when you've stepped from SolidWorks into Fusion 360 and need to look something up without leaving Claude. |
| **Three.js 3D Viewer** | `instrument-maker`, `habitat-maker` (concept renders) | Demo viewer for showing iteratively-generated 3D scenes inline. Lightweight, no install. |

## Local MCP servers (require install on your machine)

| Connector | Pairs with | Setup |
|---|---|---|
| **Blender** | `instrument-maker`, `habitat-maker`, `makerspace` (CAD-adjacent modeling, exhibition renders) | Install [Blender's MCP add-on](https://github.com/ahujasid/blender-mcp), launch Blender with the add-on enabled, then point Claude at it. Tools land as `mcp__Blender__*` — `execute_blender_code`, `get_object_detail_summary`, `render_viewport_to_path`, full Python API search. |

## Codex Desktop integrations

Codex Desktop does not currently expose the same plugin-scoped connector
install panel as Claude Desktop. When these app tools are installed in Codex,
the maker skills should use them directly and fall back to local files when
they are absent.

| Codex app/tool | Pairs with | What it adds |
|---|---|---|
| **Google Drive / Docs / Sheets / Slides** | `instrument-maker`, `sheet-metal`, `makerspace`, `sheet-music`, `habitat-maker` | Import local DOCX/XLSX/PPTX deliverables as native Google Docs, Sheets, or Slides; read comments and tables; update shared shop packets and capstone decks. |
| **GitHub** | `idea-incubator`, `instrument-maker`, `habitat-maker` | Create and inspect build issues, PRs, repo metadata, and design-book handoffs from inside Codex. |
| **Gmail** | `makerspace`, `instrument-maker`, `sheet-metal` | Draft vendor, mentor, fabricator, or shop-request emails with generated packets attached. Prefer drafts unless the user explicitly asks to send. |
| **Google Calendar** | `makerspace`, `instrument-maker`, `yoga-sequencer` | Schedule shop time, prototype reviews, build sessions, or classes after checking availability. |
| **Browser / Chrome** | `laser-art`, `habitat-maker`, `instrument-maker`, `reverse-engineer` | Verify local HTML viewers, inspect generated build-log sites, and capture screenshots for visual QA. |
| **Node REPL** | `laser-art`, `sheet-music`, `instrument-maker` | Run quick JS transforms, render checks, and lightweight asset-processing scripts without adding repo dependencies. |

## Wishlist / not yet available

- **Autodesk Fusion 360 (live model control)** — no first-party MCP yet. Watch the registry; community implementations are likely soon. For now, `Autodesk Product Help` covers docs lookup.
- **OpenSCAD** — community MCPs exist but none on the Anthropic registry. `instrument-maker` has an `openscad-master` template that pairs with manual OpenSCAD use.
- **NotebookLM** — referenced from `makerspace`'s notes; no MCP yet.

## How to install a connector

In Claude Code or Cowork:
1. Open the connectors panel (icon near the input, or `/connector`).
2. Search by name (e.g. "Wolfram").
3. Click **Connect**, complete the OAuth/API-key flow.
4. The connector's tools become available next time a `maker` skill is invoked.

## Why these aren't auto-installed

Each connector has its own auth (OAuth, API keys, account requirements). Bundling
them in the plugin would force every installer through every auth flow. Instead,
the skills inside `maker` are written to *suggest* relevant connectors at the
point a tool is needed — you'll get prompted to connect at the right moment,
not at install time.
