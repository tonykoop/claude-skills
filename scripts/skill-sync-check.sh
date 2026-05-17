#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: scripts/skill-sync-check.sh [options]

Read-only cross-device skill drift check.

Options:
  --root PATH        Add a runtime, desktop export, laptop, or staging root.
  --mode MODE       skills-meta mode: drift or inventory. Default: drift.
  --skill NAME      Focus on one skill.
  --json            Emit JSON from skills-meta.
  --list-roots      Print scanned roots and exit.
  -h, --help        Show this help.

Environment:
  SKILLS_META_ROOTS  Extra roots separated by the platform path separator.
  SKILL_SYNC_ROOTS   Extra roots for this wrapper, same separator.
  CODEX_HOME         Overrides the Codex CLI home used for default root probing.
USAGE
}

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "${script_dir}/.." && pwd)"

mode="drift"
skill=""
json=0
list_roots=0
declare -a explicit_roots=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --root)
      [[ $# -ge 2 ]] || { echo "--root requires a path" >&2; exit 2; }
      explicit_roots+=("$2")
      shift 2
      ;;
    --mode)
      [[ $# -ge 2 ]] || { echo "--mode requires drift or inventory" >&2; exit 2; }
      case "$2" in
        drift|inventory) mode="$2" ;;
        *) echo "--mode must be drift or inventory" >&2; exit 2 ;;
      esac
      shift 2
      ;;
    --skill)
      [[ $# -ge 2 ]] || { echo "--skill requires a name" >&2; exit 2; }
      skill="$2"
      shift 2
      ;;
    --json)
      json=1
      shift
      ;;
    --list-roots)
      list_roots=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

declare -a candidates=(
  "${HOME}/.claude/skills"
  "${CODEX_HOME:-${HOME}/.codex}/skills"
  "${HOME}/.codex/skills"
  "${HOME}/.gemini/skills"
)

for env_var in SKILLS_META_ROOTS SKILL_SYNC_ROOTS; do
  env_value="${!env_var:-}"
  if [[ -n "${env_value}" ]]; then
    IFS=':' read -r -a env_roots <<< "${env_value}"
    candidates+=("${env_roots[@]}")
  fi
done

candidates+=("${explicit_roots[@]}")

declare -A seen=()
declare -a roots=()
for root in "${candidates[@]}"; do
  [[ -n "${root}" ]] || continue
  expanded="${root/#\~/${HOME}}"
  [[ -d "${expanded}" ]] || continue
  if [[ -z "${seen[${expanded}]:-}" ]]; then
    seen["${expanded}"]=1
    roots+=("${expanded}")
  fi
done

if [[ "${list_roots}" -eq 1 ]]; then
  echo "repo: ${repo_root}"
  echo "readable extra roots:"
  if [[ "${#roots[@]}" -eq 0 ]]; then
    echo "- none"
  else
    for root in "${roots[@]}"; do
      echo "- ${root}"
    done
  fi
  exit 0
fi

declare -a cmd=("skills/skills-meta/scripts/skills-meta.py" "--mode" "${mode}")

if [[ -n "${skill}" ]]; then
  cmd+=("--skill" "${skill}")
  if [[ "${mode}" == "drift" ]]; then
    cmd[1]="--mode"
    cmd[2]="single"
  fi
fi

for root in "${roots[@]}"; do
  cmd+=("--root" "${root}")
done

if [[ "${json}" -eq 1 ]]; then
  cmd+=("--json")
fi

cd "${repo_root}"
python3 "${cmd[@]}"
