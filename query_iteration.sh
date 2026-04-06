#!/bin/bash

set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/github.env"

print_usage() {
  echo "Usage: $0 <iteration_number> [OPTIONS]"
  echo ""
  echo "  Fetches all issues and PRs from a GitHub Projects v2 iteration and"
  echo "  generates a metrics report via main.py."
  echo ""
  echo "Arguments:"
  echo "  <iteration_number>   The iteration number to query (e.g. 24)"
  echo ""
  echo "Options:"
  echo "  --summary            Generate an LLM summary of the iteration after fetching"
  echo "  --no-fetch           Skip data fetching and use existing cached data"
  echo "  -h, --help           Show this help message"
  echo ""
  echo "Examples:"
  echo "  $0 24"
  echo "  $0 24 --summary"
  echo "  $0 24 --no-fetch --summary"
}

if [ -z "$1" ]; then
  print_usage
  exit 0
fi

for arg in "$@"; do
  if [ "$arg" = "-h" ] || [ "$arg" = "--help" ]; then
    print_usage
    exit 0
  fi
done

ITERATION_NUM="$1"
SUMMARY_FLAG=""
NO_FETCH=false
for arg in "${@:2}"; do
  case "$arg" in
    --summary) SUMMARY_FLAG="--summary" ;;
    --no-fetch) NO_FETCH=true ;;
  esac
done
ITERATION_TITLE="Iteration $ITERATION_NUM"
OWNER="semanticarts"
API_BASE="https://api.github.com/repos/$OWNER"
TEMP_DIR="$SCRIPT_DIR/temp/iteration_${ITERATION_NUM}"

# -------------------------
# Spinner
# -------------------------
SPINNER_FRAMES=( '\' '|' '/' '-' )
SPINNER_DELAY=0.1
SPINNER_PID=""
SPINNER_MSG_FILE=$(mktemp)

set_spinner_msg() {
  echo -n "$1" > "$SPINNER_MSG_FILE"
}

start_spinner() {
  set_spinner_msg "$1"
  (
    i=0
    tput civis
    while true; do
      printf "\r%c %s" "${SPINNER_FRAMES[i]}" "$(cat "$SPINNER_MSG_FILE")"
      i=$(( (i + 1) % ${#SPINNER_FRAMES[@]} ))
      sleep "$SPINNER_DELAY"
    done
  ) &
  SPINNER_PID=$!
}

stop_spinner() {
  if [[ -n "${SPINNER_PID:-}" ]]; then
    if kill -0 "$SPINNER_PID" 2>/dev/null; then
      kill "$SPINNER_PID" 2>/dev/null || true
      wait "$SPINNER_PID" 2>/dev/null || true
    fi
    SPINNER_PID=""
    printf "\r\033[K"
    tput cnorm
  fi
  rm -f "$SPINNER_MSG_FILE"
}

trap stop_spinner EXIT INT TERM

if [ "$NO_FETCH" = true ]; then
  echo "Skipping data fetch → using existing data in $TEMP_DIR"
  source "$SCRIPT_DIR/.venv/bin/activate"
  python "$SCRIPT_DIR/main.py" "$ITERATION_TITLE" "$TEMP_DIR" $SUMMARY_FLAG
  deactivate
  exit 0
fi

# -------------------------
# Query Projects v2
# -------------------------
start_spinner "Querying $ITERATION_TITLE from Projects v2..."

ALL_NODES="[]"
CURSOR=""

while true; do
  AFTER_ARG=""
  if [ -n "$CURSOR" ]; then
    AFTER_ARG=", after: \\\"$CURSOR\\\""
  fi

  RESPONSE=$(curl -s -X POST https://api.github.com/graphql \
    -H "Authorization: Bearer $GITHUB_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
      \"query\": \"query { organization(login: \\\"semanticarts\\\") { projectV2(number: 82) { items(first: 100$AFTER_ARG) { pageInfo { hasNextPage endCursor } nodes { content { __typename ... on Issue { number title state url repository { name } } ... on PullRequest { number title state url repository { name } } } iteration: fieldValueByName(name: \\\"Iteration\\\") { ... on ProjectV2ItemFieldIterationValue { title iterationId } } status: fieldValueByName(name: \\\"Status\\\") { ... on ProjectV2ItemFieldSingleSelectValue { name } } } } } } }\"
    }")

  if echo "$RESPONSE" | jq -e '.errors' > /dev/null 2>&1; then
    stop_spinner
    echo "API error:"
    echo "$RESPONSE" | jq '.errors'
    exit 1
  fi

  PAGE_NODES=$(echo "$RESPONSE" | jq '.data.organization.projectV2.items.nodes')
  ALL_NODES=$(echo "$ALL_NODES" | jq --argjson p "$PAGE_NODES" '. + $p')

  HAS_NEXT=$(echo "$RESPONSE" | jq -r '.data.organization.projectV2.items.pageInfo.hasNextPage')
  CURSOR=$(echo "$RESPONSE" | jq -r '.data.organization.projectV2.items.pageInfo.endCursor')

  if [ "$HAS_NEXT" != "true" ]; then
    break
  fi

  set_spinner_msg "Querying $ITERATION_TITLE from Projects v2... ($(echo "$ALL_NODES" | jq 'length') items fetched)"
done

stop_spinner

ITEMS=$(echo "$ALL_NODES" | jq --arg title "$ITERATION_TITLE" '
  [.[]
  | select(.iteration | type == "object" and .title == $title)
  | {
      type: .content.__typename,
      number: .content.number,
      title: .content.title,
      state: .content.state,
      status: (.status.name // "—"),
      url: .content.url,
      repo: .content.repository.name
    }
  ]')

COUNT=$(echo "$ITEMS" | jq 'length')
echo "Found $COUNT items in $ITERATION_TITLE"
echo ""

# -------------------------
# Fetch REST metadata per item
# -------------------------
start_spinner "Fetching metadata..."

for row in $(echo "$ITEMS" | jq -r '.[] | @base64'); do
  _jq() { echo "$row" | base64 --decode | jq -r "$1"; }

  TYPE=$(_jq '.type')
  NUMBER=$(_jq '.number')
  REPO=$(_jq '.repo')
  REPO_DIR="$TEMP_DIR/$REPO"
  REPO_API="$API_BASE/$REPO"

  mkdir -p "$REPO_DIR"

  if [ "$TYPE" = "PullRequest" ]; then
    printf "\r\033[K[PR $NUMBER] $REPO\n"
    set_spinner_msg "Fetching PR $NUMBER..."

    curl -sSL \
      -H "Accept: application/vnd.github+json" \
      -H "Authorization: Bearer $GITHUB_TOKEN" \
      "$REPO_API/pulls/$NUMBER" \
      > "$REPO_DIR/pull_${NUMBER}.json"

    curl -sSL \
      -H "Accept: application/vnd.github+json" \
      -H "Authorization: Bearer $GITHUB_TOKEN" \
      "$REPO_API/pulls/$NUMBER/reviews" \
      > "$REPO_DIR/pull_reviews_${NUMBER}.json"

  elif [ "$TYPE" = "Issue" ]; then
    printf "\r\033[K[Issue $NUMBER] $REPO\n"
    set_spinner_msg "Fetching Issue $NUMBER..."

    curl -sSL \
      -H "Accept: application/vnd.github+json" \
      -H "Authorization: Bearer $GITHUB_TOKEN" \
      "$REPO_API/issues/$NUMBER" \
      > "$REPO_DIR/issue_${NUMBER}.json"

    curl -sSL \
      -H "Accept: application/vnd.github+json" \
      -H "Authorization: Bearer $GITHUB_TOKEN" \
      "$REPO_API/issues/$NUMBER/timeline" \
      > "$REPO_DIR/issue_events_${NUMBER}.json"

    # Fetch status transition details (previousStatus + status) for each transition event
    set_spinner_msg "Fetching status transitions for Issue $NUMBER..."
    TRANSITIONS="[]"
    while IFS= read -r NODE_ID; do
      RESULT=$(curl -s -X POST https://api.github.com/graphql \
        -H "Authorization: Bearer $GITHUB_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"query { node(id: \\\"$NODE_ID\\\") { ... on ProjectV2ItemStatusChangedEvent { createdAt previousStatus status } } }\"}")
      EVENT=$(echo "$RESULT" | jq '.data.node')
      TRANSITIONS=$(echo "$TRANSITIONS" | jq --argjson e "$EVENT" '. + [$e]')
    done < <(jq -r '.[] | select(.event == "project_v2_item_status_changed") | .node_id' "$REPO_DIR/issue_events_${NUMBER}.json")
    echo "$TRANSITIONS" > "$REPO_DIR/issue_status_transitions_${NUMBER}.json"

    # Fetch PRs connected to this issue via the development section
    set_spinner_msg "Fetching PRs connected to Issue $NUMBER..."
    CONNECTED_PRS=$(curl -s -X POST https://api.github.com/graphql \
      -H "Authorization: Bearer $GITHUB_TOKEN" \
      -H "Content-Type: application/json" \
      -d "{
        \"query\": \"query { repository(owner: \\\"$OWNER\\\", name: \\\"$REPO\\\") { issue(number: $NUMBER) { timelineItems(itemTypes: [CONNECTED_EVENT, CROSS_REFERENCED_EVENT], first: 25) { nodes { ... on ConnectedEvent { subject { ... on PullRequest { number repository { name } } } } ... on CrossReferencedEvent { source { ... on PullRequest { number repository { name } } } } } } } } }\"
      }")

    # Save issue → PR mapping for LLM summary generation
    echo "$CONNECTED_PRS" | jq '[
      .data.repository.issue.timelineItems.nodes[]
      | (.subject // .source)
      | select(. != null and .number != null)
      | { number: .number, repo: .repository.name }
    ] | unique_by(.number)' > "$REPO_DIR/issue_pr_map_${NUMBER}.json"

    for pr_row in $(echo "$CONNECTED_PRS" | jq -r '
      [
        .data.repository.issue.timelineItems.nodes[]
        | (.subject // .source)
        | select(. != null and .number != null)
        | { number: .number, repo: .repository.name }
      ] | unique_by(.number) | .[] | @base64'); do

      _pr_jq() { echo "$pr_row" | base64 --decode | jq -r "$1"; }
      PR_NUMBER=$(_pr_jq '.number')
      PR_REPO=$(_pr_jq '.repo')
      PR_REPO_DIR="$TEMP_DIR/$PR_REPO"
      PR_REPO_API="$API_BASE/$PR_REPO"

      mkdir -p "$PR_REPO_DIR"
      printf "\r\033[K  └─ [PR $PR_NUMBER] $PR_REPO (connected to Issue $NUMBER)\n"
      set_spinner_msg "Fetching PR $PR_NUMBER..."

      curl -sSL \
        -H "Accept: application/vnd.github+json" \
        -H "Authorization: Bearer $GITHUB_TOKEN" \
        "$PR_REPO_API/pulls/$PR_NUMBER" \
        > "$PR_REPO_DIR/pull_${PR_NUMBER}.json"

      curl -sSL \
        -H "Accept: application/vnd.github+json" \
        -H "Authorization: Bearer $GITHUB_TOKEN" \
        "$PR_REPO_API/pulls/$PR_NUMBER/reviews" \
        > "$PR_REPO_DIR/pull_reviews_${PR_NUMBER}.json"
    done
  fi
done

stop_spinner
echo "Data collection complete → $TEMP_DIR/"
echo ""

source "$SCRIPT_DIR/.venv/bin/activate"
python "$SCRIPT_DIR/main.py" "$ITERATION_TITLE" "$TEMP_DIR" $SUMMARY_FLAG
deactivate
