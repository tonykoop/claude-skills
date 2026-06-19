---
moc: shared-subassemblies
function: cross-pollination
updated: 2026-06-16
---

# MOC - Shared Subassemblies

Story #244 of the Cross-Pollination Engine (epic #236). This is an Obsidian
**Map of Content** that groups ideas by the `functions:` / `interfaces:` tags
defined in [functional-tagging-schema](../functional-tagging-schema.md) (#243)
and surfaces where the same subassembly recurs across projects.

Drop this note into your Obsidian vault (e.g. `MOCs/Shared Subassemblies.md`).
It is the human-facing dashboard; the Cross-Pollination Agent (#247) is the
automated counterpart.

> **Outside Obsidian?** The Dataview/dataviewjs blocks below only render inside
> Obsidian with the Dataview plugin. For Codex/Gemini CLI, CI, or a quick
> terminal check, [`../../scripts/shared_subassemblies.py`](../../scripts/shared_subassemblies.py)
> reproduces these same views (shared subassemblies, shared interfaces,
> cross-pollination candidate pairs) from the `functions:` / `interfaces:`
> frontmatter — `shared_subassemblies.py --dir <notes>` (add `--json` for a
> machine-readable form). It's the portable, unit-tested twin of this MOC.

## Setup

- **Required plugin:** [Dataview](https://github.com/blacksmithgu/obsidian-dataview)
  (Community Plugins -> Browse -> "Dataview" -> Install -> Enable).
- **Required for `dataviewjs` blocks:** in Dataview settings, enable
  **"Enable JavaScript Queries"**.
- **Assumption:** every idea note carries the frontmatter from #243, with
  `functions:` as a YAML list. Notes without `functions:` are invisible to
  these queries by design - that is the nudge to tag at intake.
- **Folder scope:** the queries below scan the whole vault. Narrow them by
  adding `FROM "Ideas"` (or your folder) after the `TABLE`/`LIST` clause.

## 1. Every function, and which ideas perform it

The core "shared subassembly" view: each row is one function, with the count of
ideas that perform it and links to them. A function with 2+ ideas is a
cross-pollination opportunity.

````markdown
```dataview
TABLE length(rows) AS "# ideas", rows.file.link AS "Ideas"
FROM ""
FLATTEN functions AS fn
WHERE fn
GROUP BY fn AS "Function"
SORT length(rows) DESC
```
````

## 2. Hot functions only (shared across 2+ ideas)

The same view, filtered to functions that actually recur. This is the short
list worth a Universal Interface (#245) or a circuits-inventory entry (#248).

````markdown
```dataviewjs
const pages = dv.pages().where(p => p.functions);
const byFn = {};
for (const p of pages) {
  for (const fn of (Array.isArray(p.functions) ? p.functions : [p.functions])) {
    (byFn[fn] ??= []).push(p.file.link);
  }
}
const rows = Object.entries(byFn)
  .filter(([, links]) => links.length >= 2)
  .sort((a, b) => b[1].length - a[1].length)
  .map(([fn, links]) => [fn, links.length, links]);
dv.table(["Function", "# ideas", "Ideas"], rows);
```
````

## 3. Shared interfaces (the Lego sockets)

Groups ideas by `interfaces:` value, so you can see which mounting patterns,
fasteners, and connectors already recur - the raw material for the Universal
Interface guide (#245).

````markdown
```dataview
TABLE length(rows) AS "# ideas", rows.file.link AS "Ideas"
FROM ""
FLATTEN interfaces AS iface
WHERE iface
GROUP BY iface AS "Interface"
SORT length(rows) DESC
```
````

## 4. Cross-pollination candidate pairs

Finds pairs of ideas that share at least one function but live in different
domains - the highest-signal "a solved this, b needs it" matches. This mirrors
the agent's heuristic (#247) so you can spot-check it by hand.

````markdown
```dataviewjs
const pages = dv.pages().where(p => p.functions).array();
const norm = a => Array.isArray(a) ? a : (a ? [a] : []);
const seen = new Set();
const rows = [];
for (let i = 0; i < pages.length; i++) {
  for (let j = i + 1; j < pages.length; j++) {
    const a = pages[i], b = pages[j];
    const fa = new Set(norm(a.functions));
    const shared = norm(b.functions).filter(f => fa.has(f));
    if (shared.length === 0) continue;
    if ((a.domain ?? "") === (b.domain ?? "")) continue; // cross-domain only
    const key = [a.file.path, b.file.path].sort().join("|");
    if (seen.has(key)) continue;
    seen.add(key);
    rows.push([a.file.link, b.file.link, shared.join(", "), shared.length]);
  }
}
rows.sort((x, y) => y[3] - x[3]);
dv.table(["Idea A", "Idea B", "Shared functions", "#"], rows.map(r => r.slice(0, 3).concat(r[3])));
```
````

## 5. Already-solved primitives (reuse now)

Ideas that carry a `solved-in:` back-link are proven primitives. Surface them so
a new idea can reuse instead of reinvent. These rows feed the circuits
inventory (#248).

````markdown
```dataview
TABLE solved-in AS "Solved in", functions AS "Functions", maturity AS "Maturity"
FROM ""
WHERE solved-in
SORT maturity DESC
```
````

## 6. Untagged ideas (fix these)

Notes missing `functions:` cannot cross-pollinate. This query is the to-do list
for backfilling tags per the #243 intake checklist.

````markdown
```dataview
LIST
FROM ""
WHERE !functions AND (status OR idea)
```
````

## Reading the dashboard

- A function in query 2 with 3+ ideas is a strong candidate for a Universal
  Interface (#245) and a circuits-inventory entry (#248).
- A pair in query 4 is a literal cross-pollination suggestion; if the agent
  (#247) has not already posted it, post it by hand.
- Anything in query 6 is a tagging debt - close the loop at intake, not here.
