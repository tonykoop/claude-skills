#!/usr/bin/env bash
# Convert GitHub issue labels into sprint batch and model recommendations.

set -euo pipefail

INPUT="-"
DEFAULT_MODEL="o4-mini"
STRONG_MODEL="gpt-5.5"
FORMAT="markdown"

usage() {
  cat <<'EOF'
Plan label-aware sprint batches from GitHub issue JSON.

Usage:
  plan-label-batches.sh [--input FILE] [--default-model MODEL] [--strong-model MODEL] [--format markdown|json]

Input:
  Reads GitHub issue JSON from stdin by default. Accepts a single issue object,
  an array of issue objects, or an object with an "issues", "items", or "nodes"
  array. This matches common gh output such as:

    gh issue list --json number,title,url,labels | bash scripts/plan-label-batches.sh
    gh issue view 47 --json number,title,url,labels | bash scripts/plan-label-batches.sh

Label families:
  skill:*       primary lane when no batch:* label is present
  artifact:*    deliverable or validation note
  risk:*        risk note; high/architecture/ambiguity prefer the strong model
  readiness:*   readiness note
  model:*       suggested model; conflicts become manager-review
  batch:*       explicit sprint batch note and group
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --input) INPUT="$2"; shift 2 ;;
    --default-model) DEFAULT_MODEL="$2"; shift 2 ;;
    --strong-model) STRONG_MODEL="$2"; shift 2 ;;
    --format) FORMAT="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Error: unknown arg: $1" >&2; usage >&2; exit 2 ;;
  esac
done

case "$FORMAT" in
  markdown|json) ;;
  *) echo "Error: --format must be markdown or json" >&2; exit 2 ;;
esac

command -v jq >/dev/null 2>&1 || {
  echo "Error: jq is required to plan label-aware batches" >&2
  exit 1
}

if [[ "$INPUT" == "-" ]]; then
  payload="$(cat)"
else
  [[ -r "$INPUT" ]] || { echo "Error: input is not readable: $INPUT" >&2; exit 1; }
  payload="$(cat "$INPUT")"
fi

# shellcheck disable=SC2016
planner='
def issue_array:
  if type == "array" then .
  elif type == "object" and has("issues") then .issues
  elif type == "object" and has("items") then .items
  elif type == "object" and has("nodes") then .nodes
  elif type == "object" and has("number") then [.]
  else error("input must be an issue object or issue array")
  end;

def label_names:
  (.labels // [])
  | map(if type == "object" then .name else . end)
  | map(select(. != null and . != ""))
  | unique;

def family($labels; $name):
  [$labels[] | select(startswith($name + ":")) | sub("^" + $name + ":"; "")];

def strong_label($labels):
  any($labels[];
    . == "risk:high" or
    . == "risk:architecture" or
    . == "risk:ambiguity" or
    . == "batch:needs-review" or
    . == "artifact:validation-loop"
  );

def preferred_model($labels):
  (family($labels; "model")) as $models
  | if ($models | length) == 1 then $models[0]
    elif ($models | length) > 1 then "manager-review"
    elif strong_label($labels) then $strong_model
    else $default_model
    end;

def batch_group($labels):
  (family($labels; "batch")) as $batch
  | (family($labels; "skill")) as $skill
  | if ($batch | length) > 0 then $batch[0]
    elif ($skill | length) > 0 then $skill[0]
    else "general"
    end;

def batch_notes($labels):
  (family($labels; "skill")) as $skill
  | (family($labels; "artifact")) as $artifact
  | (family($labels; "risk")) as $risk
  | (family($labels; "readiness")) as $readiness
  | (family($labels; "batch")) as $batch
  | (family($labels; "model")) as $models
  | [
      (if ($skill | length) > 0 then "lane " + ($skill | join(",")) else empty end),
      ($artifact[]? | "artifact " + .),
      ($risk[]? | "risk " + .),
      ($readiness[]? | "readiness " + .),
      (if ($models | length) > 1 then "model conflict requires manager review" else empty end),
      ($batch[]? | if . == "needs-review" then "needs review before merge" else "batch " + . end)
    ]
  | if length > 0 then join("; ") else "no routing labels" end;

def issue_ref:
  ("#" + (.number | tostring) + " " + (.title // "untitled")) as $text
  | if (.url // "") != "" then "[" + $text + "](" + .url + ")" else $text end;

def markdown_cell:
  tostring | gsub("\\|"; "\\|") | gsub("\r?\n"; " ");

def label_cell:
  if length > 0 then join(", ") else "(none)" end;

def planned_issue:
  label_names as $labels
  | {
      issue: issue_ref,
      number,
      title: (.title // ""),
      url: (.url // ""),
      labels: $labels,
      batch: batch_group($labels),
      suggested_model: preferred_model($labels),
      batch_notes: batch_notes($labels)
    };

issue_array | map(planned_issue)
'

if [[ "$FORMAT" == "json" ]]; then
  jq --arg default_model "$DEFAULT_MODEL" --arg strong_model "$STRONG_MODEL" "$planner" <<<"$payload"
else
  printf '| Issue | Labels | Batch | Suggested model | Batch notes |\n'
  printf '| --- | --- | --- | --- | --- |\n'
  jq -r --arg default_model "$DEFAULT_MODEL" --arg strong_model "$STRONG_MODEL" "$planner | .[] | [ .issue, (.labels | label_cell), .batch, .suggested_model, .batch_notes ] | \"| \" + (map(markdown_cell) | join(\" | \")) + \" |\"" <<<"$payload"
fi
