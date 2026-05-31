#!/usr/bin/env bash
# deploy_interactive.sh — CloudDeploy each model's Manipulate as a PUBLIC interactive app.
#
# Why this exists: wolfram_sync.wls uploads .wl SOURCE (renders as code, not interactive).
# To get a live interactive embed you must CloudDeploy the Manipulate. This deploys, per
# model, to Musical_Instruments/<category>/<repo>/<repo>-interactive and records the URLs
# in manifest/wolfram_interactive_urls.json (which generate_explorer.py reads as --embed-urls).
#
# Robust recipe (validated 2026-05-31):
#   mani = Get[model]           (model defines functions; SaveDefinitions->True on its
#                                Manipulate bundles them so they travel to the cloud)
#   If Head[mani]===Manipulate            -> deploy mani
#   elif AssociationQ[mani]               -> deploy the Manipulate-valued entry (e.g. "explorer")
#   CloudDeploy[mani, target, Permissions->"Public"]
#
# Per-repo isolated wolframscript invocations (one bad model can't kill the batch; the
# harmless segfault-on-teardown happens AFTER the deploy + URL print).
#
# Usage: ./deploy_interactive.sh <GitHub-root>
#   Requires: wolframscript -authenticate (done once). Run from WSL where paths resolve.
set -u
ROOT="${1:-/mnt/c/Users/Tony/Documents/GitHub}"
OUT="$(dirname "$0")/manifest/wolfram_interactive_urls.json"
declare -A CAT=( [strings]=strings [woodwind]=woodwinds [brass]=brass [percussion]=percussion [idiophones]=idiophones )
echo "[" > "$OUT.tmp"; first=1
while IFS= read -r mf; do
  rel="${mf#$ROOT/}"; fam=$(echo "$rel" | cut -d/ -f2); repo=$(basename "$(dirname "$(dirname "$mf")")")
  cat="${CAT[$fam]:-unsorted}"; target="Musical_Instruments/$cat/$repo/$repo-interactive"
  url=$(timeout 90 wolframscript -code "SetDirectory[DirectoryName[\"$mf\"]]; r=Get[\"$mf\"]; m=If[Head[r]===Manipulate,r,If[AssociationQ[r],SelectFirst[Values[r],Head[#]===Manipulate&,Null],Null]]; If[Head[m]===Manipulate, Print[\"URLOUT=\",First[CloudDeploy[m,\"$target\",Permissions->\"Public\"]]], Print[\"URLOUT=SKIP\"]]" 2>/dev/null | grep -oE 'URLOUT=.*' | sed 's/URLOUT=//' | head -1)
  [[ "$url" == https://* ]] || { echo "SKIP $repo ($url)"; continue; }
  [ $first -eq 1 ] || echo "," >> "$OUT.tmp"; first=0
  printf '{"repo":"%s","source_file":"wolfram/%s-wolfram-model.wl","cloud_path":"%s","cloud_url":"%s","permission":"Public-Execute"}' "$repo" "$repo" "$target" "$url" >> "$OUT.tmp"
  echo "deployed $repo -> $url"
done < <(find "$ROOT/instruments" -path '*/wolfram/*-wolfram-model.wl' 2>/dev/null | grep -v '/.git/')
echo "]" >> "$OUT.tmp"; mv "$OUT.tmp" "$OUT"
echo "wrote $OUT"
