# S8 decision — tool-matrix promotion (issue #219)

> **Decision:** PROMOTE. The Alpha tool-matrix schema is promoted into the
> **makerspace** skill as the single source of truth. The Evolution
> Pipeline's *Alpha Workspace Compiler* consumes it; it does not define a
> private copy.
>
> Decided 2026-06-15. Gates `compile_alpha` hardening (issue #219).

## The question

Should the Alpha tool-matrix schema live inside the `evolution-pipeline`
skill (private to the compiler), or be promoted into the `makerspace` skill
so both sides share one source of truth? (Refs #206, #219; original gap
list in the Evolution Pipeline `makerspace-gaps.md` / `follow-up-stories.md`.)

## Finding that shaped the call

At decision time **no Alpha tool-matrix schema existed yet** in either
`tonykoop/claude-skills` or `tonykoop/StudioPipeline` — the
`evolution-pipeline` skill and its `follow-up-stories.md` /
`makerspace-gaps.md` were referenced in #206/#219 but not yet authored.
So this is not a "move existing code" decision; it is a "decide the home
before the schema is written" decision. That removes migration cost from
the equation and lets us put the schema in the right place from the start.

## Why promote (rationale)

1. **makerspace already owns the tool inventory.** The space profile
   (`references/space-profile-schema.md`, `spaces/<slug>/profile.yaml`)
   already models tools with stable ids, categories, specs, material
   allow/ban lists, certs, and reservations. A tool-matrix is a *projection*
   of that data, not new data. Defining it inside evolution-pipeline would
   fork the inventory model and invite drift.

2. **"User's local tool matrix" IS a makerspace concept.** Issue #206
   describes the Alpha Workspace Compiler as "downgrade master CAD fidelity
   to the user's local tool matrix." That tool matrix is exactly what
   makerspace exists to reason about (make/order/buy/borrow, machine-aware
   process plans, workholding/tolerance). Capability-of-the-shop is
   makerspace's home turf.

3. **One source of truth beats two.** If both skills carried a tool-matrix
   schema, every category-enum or envelope-field change would need a
   two-repo sync (claude-skills + StudioPipeline). Promotion keeps the
   schema in one repo; evolution-pipeline pins the makerspace version it
   validated against.

4. **Clean dependency direction.** makerspace has no dependency on the
   Evolution Pipeline and can ship the schema standalone (useful even
   without the compiler). evolution-pipeline depends *down* onto makerspace,
   which matches the plugin layering (maker plugin = stable shop primitives;
   StudioPipeline = higher-level pipeline that builds on them).

5. **No vendoring / no 4th plugin.** Promotion lands as a reference +
   version bump inside the existing maker plugin. It does not require a new
   plugin, and it does not vendor StudioPipeline into the maker plugin.

## Why NOT keep it in evolution-pipeline

- It would duplicate the inventory model already in makerspace.
- It would couple a stable shop primitive (what can my shop make?) to an
  unshipped higher-level pipeline.
- It would force cross-repo schema syncs forever.

The only argument *for* keeping it private — "the compiler can iterate
fast without a makerspace release" — is weak, because the schema is small,
stable-shaped (it mirrors the existing tools enum), and versioned; the
compiler pins a version and is unaffected by makerspace iterating elsewhere.

## What this decision implements (in makerspace)

- `references/tool-matrix-schema.md` — the promoted schema (source of
  truth), expressed as a derived capability view over the space profile,
  with a `process` enum that maps onto the existing `category` enum.
- This decision record.
- makerspace version bump + CHANGELOG entry registering the new reference.

## What the Evolution Pipeline side must do (when authored)

- Reference `makerspace/references/tool-matrix-schema.md` as the schema; do
  not redefine it.
- Pin the makerspace skill version it validated `compile_alpha` against.
- Add a generator that projects a chosen space profile into a
  `tool-matrix.yaml` (see "Generating a tool-matrix" in the schema doc).

## Boundary / invariant

This change stays inside `plugins/maker/skills/makerspace/`. No new plugin,
no StudioPipeline vendoring. The manifest `canonical_version` for makerspace
should advance with this bump (handled by the manifest-sync lane to keep
manifest edits append-only and conflict-free).
