# Recommended connectors for the `coding` plugin

These connectors aren't required, but each one unlocks specific skills inside
the `coding` plugin. Connect any of them from Claude's connector registry
(search by name, click Connect, follow the auth flow). Skills will start
calling them automatically once they're available.

## Hosted connectors (one-click from registry)

| Connector | Pairs with | What it adds |
|---|---|---|
| **Context7** | every skill that touches an unfamiliar library or framework | "Up-to-date docs for LLMs." `resolve-library-id` + `query-docs` give Claude live, version-pinned API reference instead of training-data drift. Especially useful in `merge-review` (verifying API usage in a diff) and `scaffold-hygiene` (cross-checking framework migration paths). |
| **GitHub** | `merge-review`, `sprint-update`, `tmux-sprint`, `run-swarm`, `ci-triage`, `scaffold-hygiene`, `idea-incubator` | The whole sprint stack assumes a GitHub backend — issues, PRs, CI checks, branches, releases. Connect this and most coding skills become real instead of advisory. |
| **Linear** | `sprint-update`, `tmux-sprint` (Linear-backed Queue columns), `idea-incubator` (promote to Linear instead of GitHub issues) | Drop-in alternative to (or supplement to) GitHub Issues. `sprint-update` can read Linear cycles for capacity planning. |
| **Datadog** | `ci-triage`, `sprint-supervisor` (overnight watch), incident workflows | Log search, metrics, monitor state, event correlation. When CI breaks "but only in prod," this is the connector that closes the loop. |
| **Exa** | every skill that does research before acting | Web + code-context search optimized for code. Cheap fallback when Context7 doesn't have a library indexed. |
| **Microsoft Learn** | `merge-review` and `scaffold-hygiene` on .NET / Azure / TypeScript stacks | First-party Microsoft docs, fetchable on demand. |
| **Vercel** | deploy-adjacent flows in `merge-review` and `ci-triage` | Project + deployment + deployment-event lookup. Pairs with the `engineering:deploy-checklist` skill if you have it. |
| **Cloudflare Developer Platform** | infra-touching diffs in `merge-review` | Workers, KV, R2 binding inspection — confirms the deploy diff actually matches the infra change. |
| **PlanetScale** | migration-touching PRs in `merge-review`, data-shape audits in `scaffold-hygiene` | Branch schema reads, query execution. Mostly read-only, safe to wire into review flows. |
| **Atlassian** (Jira, Confluence) | `sprint-update`, `idea-incubator` (org-flavored issue tracker) | If your team isn't on GitHub Issues or Linear, this is the third option. |
| **Slack** | `sprint-supervisor` (morning summary delivery), `run-swarm` (manager-pane notifications), `merge-review` (PR ping to channel) | Push the artifacts your skills produce into the channel where standups already happen. |
| **Notion** | `idea-incubator` (workspace alt to GitHub issues), `scaffold-hygiene` runbooks, `sprint-update` docs | If the team's source of truth is Notion. |

## Wishlist / not yet available

- **Codecov / Coveralls** — coverage delta for `merge-review`. No registry connector yet.
- **Sentry** — error-rate-aware deploy checks for `ci-triage` and `sprint-supervisor`. Not on the registry as of writing.
- **Buildkite / CircleCI** — CI providers other than GitHub Actions for `ci-triage`. None on the registry yet.

## How to install a connector

In Claude Code or Cowork:
1. Open the connectors panel (icon near the input, or `/connector`).
2. Search by name (e.g. "Context7").
3. Click **Connect**, complete the OAuth/API-key flow.
4. The connector's tools become available next time a `coding` skill is invoked.

## Why these aren't auto-installed

Each connector has its own auth (OAuth, API keys, account requirements). The
sprint and CI skills assume *your* GitHub org, *your* Datadog account, *your*
Linear workspace. Bundling specific configs would either fail for everyone
or leak someone else's setup. Instead, skills suggest connectors at the
point a tool is needed.
