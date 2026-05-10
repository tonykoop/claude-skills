#!/usr/bin/env bash
# twingrid-lane-matrix.sh
#
# Read-only manager helper: walks /tmp/twingrid-r<N>-* output folders and
# emits a per-lane matrix as TSV (default) or JSON. Pairs Claude side A
# with Codex side B by lane name.
#
# The matrix row schema lives at:
#   docs/twingrid/lane-matrix-row.schema.yaml
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: twingrid-lane-matrix.sh --round N [options]

Required:
  --round N           Round number. Scans /tmp/twingrid-r<N>-* directories.

Options:
  --root DIR          Directory to scan. Default: /tmp.
  --format FMT        tsv (default) or json.
  -h, --help          Show this help.

Output columns (TSV) or keys (JSON):
  round lane a_runtime a_folder a_artifacts a_record a_peek a_skill_imp
        a_blocked b_runtime b_folder b_artifacts b_record b_peek b_skill_imp
        b_blocked

Notes:
- Pairing is by lane name extracted from the folder name pattern
  twingrid-r<N>-<runtime>-<lane>-<slug>. Lanes that match in any of the
  manager's known lane lists (alice/bob/cindy/dan/elsa/frank/gina/henry/irene)
  are paired; unknown-lane folders are reported in their own rows.
USAGE
}

round=""
root="/tmp"
format="tsv"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --round) [[ $# -ge 2 ]] || { echo "--round requires N" >&2; exit 2; }
             round="$2"; shift 2 ;;
    --root)  [[ $# -ge 2 ]] || { echo "--root requires DIR" >&2; exit 2; }
             root="$2"; shift 2 ;;
    --format) [[ $# -ge 2 ]] || { echo "--format requires tsv|json" >&2; exit 2; }
              format="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown arg: $1" >&2; usage >&2; exit 2 ;;
  esac
done

[[ -n "$round" ]] || { echo "--round is required" >&2; exit 2; }
[[ "$format" == "tsv" || "$format" == "json" ]] || \
  { echo "--format must be tsv or json" >&2; exit 2; }

# Known lanes. Easy to extend.
known_lanes=(alice bob cindy dan elsa frank gina henry irene)

# Helper: extract lane from a folder basename.
extract_lane() {
  local base="$1" lane
  for lane in "${known_lanes[@]}"; do
    if [[ "$base" == *"-${lane}-"* || "$base" == *"-${lane}" ]]; then
      printf '%s\n' "$lane"; return 0
    fi
  done
  printf '%s\n' "unknown"
}

# Helper: extract runtime from a folder basename.
extract_runtime() {
  local base="$1"
  if   [[ "$base" == *"-claude-"* ]]; then printf 'claude-code\n'
  elif [[ "$base" == *"-codex-"*  ]]; then printf 'codex\n'
  elif [[ "$base" == *"-gemini-"* ]]; then printf 'gemini\n'
  else printf 'other\n'
  fi
}

# Helper: count files in a folder (excluding dotfiles).
count_files() {
  local dir="$1"
  [[ -d "$dir" ]] || { printf '0\n'; return 0; }
  find "$dir" -maxdepth 1 -type f ! -name '.*' -printf '.' | wc -c | tr -d ' '
}

# Helper: presence checks for canonical artifacts.
has_agent_record() {
  local dir="$1"
  [[ -d "$dir" ]] || return 1
  shopt -s nullglob
  local hits=( "$dir"/agent_record.json "$dir"/agent_record.yaml \
               "$dir"/*agent_record*.md "$dir"/09_*agent_record*.md \
               "$dir"/09_twingrid_agent_record.md )
  shopt -u nullglob
  [[ ${#hits[@]} -gt 0 ]]
}

has_partner_peek_record() {
  local dir="$1"
  [[ -d "$dir" ]] || return 1
  [[ -f "$dir/partner-peek-record.json" || -f "$dir/partner-peek-record.yaml" ]]
}

has_skill_improvement() {
  local dir="$1"
  [[ -d "$dir" ]] || return 1
  shopt -s nullglob
  local hits=( "$dir"/skill-improvement-proposal* "$dir"/skill_improvement* \
               "$dir"/*skill-improvement* )
  shopt -u nullglob
  [[ ${#hits[@]} -gt 0 ]]
}

has_blocked_marker() {
  local dir="$1"
  [[ -d "$dir" ]] || return 1
  [[ -f "$dir/BLOCKED.txt" ]]
}

# Scan root for matching folders.
declare -A a_folder_for b_folder_for

shopt -s nullglob
for d in "$root"/twingrid-r"${round}"-*; do
  [[ -d "$d" ]] || continue
  base="$(basename "$d")"
  lane="$(extract_lane "$base")"
  runtime="$(extract_runtime "$base")"
  case "$runtime" in
    claude-code) a_folder_for["$lane"]="$d" ;;
    codex)       b_folder_for["$lane"]="$d" ;;
    *)           # unknown side; park as A if A unset, else B.
                 if [[ -z "${a_folder_for[$lane]:-}" ]]; then
                   a_folder_for["$lane"]="$d"
                 else
                   b_folder_for["$lane"]="$d"
                 fi
                 ;;
  esac
done
shopt -u nullglob

# Lane order for output.
mapfile -t lanes_seen < <(printf '%s\n' "${!a_folder_for[@]}" "${!b_folder_for[@]}" | sort -u)

emit_tsv_header() {
  printf 'round\tlane\ta_runtime\ta_folder\ta_artifacts\ta_record\ta_peek\ta_skill_imp\ta_blocked\tb_runtime\tb_folder\tb_artifacts\tb_record\tb_peek\tb_skill_imp\tb_blocked\n'
}

bool_str() { if "$@"; then printf 'true'; else printf 'false'; fi; }

emit_row() {
  local lane="$1"
  local a="${a_folder_for[$lane]:-}"
  local b="${b_folder_for[$lane]:-}"
  local a_runtime b_runtime
  a_runtime=""; b_runtime=""
  [[ -n "$a" ]] && a_runtime="$(extract_runtime "$(basename "$a")")"
  [[ -n "$b" ]] && b_runtime="$(extract_runtime "$(basename "$b")")"

  local a_count b_count
  a_count="$(count_files "$a")"
  b_count="$(count_files "$b")"

  local a_rec a_peek a_skill a_blk b_rec b_peek b_skill b_blk
  a_rec="$(  bool_str has_agent_record         "$a")"
  a_peek="$( bool_str has_partner_peek_record  "$a")"
  a_skill="$(bool_str has_skill_improvement    "$a")"
  a_blk="$(  bool_str has_blocked_marker       "$a")"
  b_rec="$(  bool_str has_agent_record         "$b")"
  b_peek="$( bool_str has_partner_peek_record  "$b")"
  b_skill="$(bool_str has_skill_improvement    "$b")"
  b_blk="$(  bool_str has_blocked_marker       "$b")"

  if [[ "$format" == "tsv" ]]; then
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
      "$round" "$lane" "$a_runtime" "$a" "$a_count" "$a_rec" "$a_peek" "$a_skill" "$a_blk" \
      "$b_runtime" "$b" "$b_count" "$b_rec" "$b_peek" "$b_skill" "$b_blk"
  else
    # JSON: emit one object per row, comma-handling done by caller.
    jq -n --arg round "$round" --arg lane "$lane" \
          --arg a_runtime "$a_runtime" --arg a_folder "$a" \
          --argjson a_artifacts "$a_count" \
          --argjson a_record "$a_rec" --argjson a_peek "$a_peek" \
          --argjson a_skill "$a_skill" --argjson a_blocked "$a_blk" \
          --arg b_runtime "$b_runtime" --arg b_folder "$b" \
          --argjson b_artifacts "$b_count" \
          --argjson b_record "$b_rec" --argjson b_peek "$b_peek" \
          --argjson b_skill "$b_skill" --argjson b_blocked "$b_blk" \
          '{
             round: ($round | tonumber),
             lane: $lane,
             a_runtime: $a_runtime,
             a_output_folder: $a_folder,
             a_artifact_count: $a_artifacts,
             a_agent_record_present: $a_record,
             a_partner_peek_record_present: $a_peek,
             a_skill_improvement_recommended: $a_skill,
             a_blocked_marker_present: $a_blocked,
             b_runtime: $b_runtime,
             b_output_folder: $b_folder,
             b_artifact_count: $b_artifacts,
             b_agent_record_present: $b_record,
             b_partner_peek_record_present: $b_peek,
             b_skill_improvement_recommended: $b_skill,
             b_blocked_marker_present: $b_blocked,
             notes: ""
           }'
  fi
}

if [[ "$format" == "tsv" ]]; then
  emit_tsv_header
  for lane in "${lanes_seen[@]}"; do
    emit_row "$lane"
  done
else
  printf '['
  first=1
  for lane in "${lanes_seen[@]}"; do
    if [[ "$first" -eq 1 ]]; then first=0; else printf ','; fi
    emit_row "$lane"
  done
  printf ']\n'
fi
