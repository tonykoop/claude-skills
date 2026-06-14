# Rollout & Coverage Audit

The first pass is a **handful of repos (3–5)** to confirm the pattern before
scaling. The pilot set used to validate this skill was: `transverse-flute`
(woodwind/bore physics), `tongue-drum` (idiophone), `kora` (string+resonator),
and `handpan` (tuned metal, high uncertainty). These span the main physics
families, so a pattern that works across them generalizes.

## Recommended order for the full rollout

1. **Public "done-bar" repos first.** The repos already held up as examples
   (tongue-drum, gemshorn, udu, ocarina, transverse-flute) are the ones outside
   readers actually land on. Cite these first for the highest credibility
   return.
2. **Repos with a populated design sheet or validation data next.** If a repo
   already has measured-vs-predicted data, its citations almost write
   themselves — the sources are whatever produced those predictions.
3. **Scaffold-only / early repos last**, or skip until they have real content.
   A citation file on an empty repo is premature.

## Batch coverage audit

To find which repos still lack attribution, iterate over the GitHub folder and
classify each repo:

```bash
# pseudo-pattern; run on the PC where the repos live
for repo in */ ; do
  if [ ! -f "$repo/.citations.yaml" ]; then
    echo "MISSING  $repo  (no .citations.yaml)"
  elif ! python3 scripts/gen_sources.py check references/registry.yaml "$repo" >/dev/null 2>&1; then
    echo "INVALID  $repo  (.citations.yaml present but fails check)"
  elif [ ! -f "$repo/SOURCES.md" ]; then
    echo "UNBUILT  $repo  (valid citations, SOURCES.md not generated)"
  else
    echo "OK       $repo"
  fi
done
```

This four-state report (MISSING / INVALID / UNBUILT / OK) is the coverage
dashboard. Drive it to zero MISSING on the public repos first.

## Keeping SOURCES.md current

- `SOURCES.md` is generated; never hand-edit it. Edit `.citations.yaml` and
  regenerate. The footer of every `SOURCES.md` says so.
- When the registry refreshes (new sources, fixed URLs), repos do **not** need
  regenerating unless they cite a changed entry — the link lives in the
  registry. Regenerate a repo only when its `.citations.yaml` changes or a key
  it cites was edited.
- Consider a CI check (or a pre-commit hook) that runs `gen_sources.py check`
  on any repo containing `.citations.yaml`, so an invalid citation never lands.
