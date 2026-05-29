#!/usr/bin/env bash
set -euo pipefail

repo="${1:-${GITHUB_REPOSITORY:-}}"
if [[ -z "${repo}" ]]; then
  echo "usage: $0 owner/repo" >&2
  exit 1
fi

if ! command -v gh >/dev/null 2>&1; then
  echo "gh is required for label bootstrap" >&2
  exit 1
fi

labels=(
  "capture|Fresh idea captured from Telegram, chat, or a quick note.|1d76db"
  "intake|A pasted dump that still needs parsing into separate ideas.|0e8a16"
  "connect|Link this idea to related issues or duplicates.|5319e7"
  "review|Backlog review or triage pass.|fbca04"
  "promote|Ready for downstream handoff.|b60205"
  "needs-clarification|Key detail is missing before the idea can move.|d93f0b"
  "duplicate-candidate|This idea may overlap with an existing issue.|e11d21"
  "stale|The idea has sat long enough to deserve a review.|c2c2c2"
  "ready-now|Low-friction idea that can be executed quickly.|0052cc"
  "maker|Fabrication, shop, or hardware ideas.|bfdadc"
  "instrument|Musical instrument ideas and acoustics work.|c5def5"
  "yoga|Class, sequence, or movement ideas.|f9d0c4"
  "skills|Skill ecosystem, tooling, or orchestration ideas.|d4c5f9"
  "general|Idea does not fit a narrower domain.|ededed"
)

for entry in "${labels[@]}"; do
  IFS='|' read -r name description color <<<"${entry}"
  gh label create "${name}" \
    --repo "${repo}" \
    --description "${description}" \
    --color "${color}" \
    --force >/dev/null
done

echo "Created ${#labels[@]} labels in ${repo}"
