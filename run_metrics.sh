#!/usr/bin/env bash
set -euo pipefail

# Get to this directory, in case this file is executed from a random place
cd "$(dirname "$0")"
mkdir -p temp

# Load the environment variable(s) from github.env
source github.env

if [[ -z "${GITHUB_TOKEN:-}" ]]; then
  echo "GITHUB_TOKEN is not set. Did you source github.env?"
  exit 1
fi

NOW=$(date +%s)

# Quick check on the PAT exp. date
if [ "$NOW" -ge "$EXPIRED_DATE" ]; then
  echo "Personal Access Token has expired. Cannot run the script."
  exit 1
fi

# -------------------------
# Configuration
# -------------------------
OWNER="semanticarts"
API_BASE="https://api.github.com/repos/$OWNER"
TEMP_DIR="temp"

# -------------------------
# Argument parsing
# -------------------------
for arg in "$@"; do
  case "$arg" in
    --repo)
      MODE="repo"
      ;;
    --prs)
      MODE="prs"
      ;;
    --issues)
      MODE="issues"
      ;;
    *)
      case "$MODE" in
        repo)
          REPO="$arg"
          ;;
        prs)
          PRS+=("$arg")
          ;;
        issues)
          ISSUES+=("$arg")
          ;;
        *)
          echo "Unknown argument: $arg"
          exit 1
          ;;
      esac
      ;;
  esac
done

if [[ -z "${REPO:-}" ]]; then
  echo "--repo is required (e.g. dca, QuickBooks)"
  exit 1
fi

REPO_DIR="$TEMP_DIR/$REPO"
mkdir -p "$TEMP_DIR/$REPO"

REPO_API="$API_BASE/$REPO"

# -------------------------
# Fetch PR data
# -------------------------
for PR in "${PRS[@]}"; do
  echo "[$REPO] Fetching PR $PR"

  curl -sSL \
    -H "Accept: application/vnd.github+json" \
    -H "Authorization: Bearer $GITHUB_TOKEN" \
    "$REPO_API/pulls/$PR" \
    > "$REPO_DIR/pull_${PR}.json"

  curl -sSL \
    -H "Accept: application/vnd.github+json" \
    -H "Authorization: Bearer $GITHUB_TOKEN" \
    "$REPO_API/pulls/$PR/reviews" \
    > "$REPO_DIR/pull_reviews_${PR}.json"
done

# -------------------------
# Fetch Issue data
# -------------------------
for ISSUE in "${ISSUES[@]}"; do
  echo "[$REPO] Fetching Issue $ISSUE"

  curl -sSL \
    -H "Accept: application/vnd.github+json" \
    -H "Authorization: Bearer $GITHUB_TOKEN" \
    "$REPO_API/issues/$ISSUE" \
    > "$REPO_DIR/issue_${ISSUE}.json"

  ISSUE_JSON="$REPO_DIR/issue_${ISSUE}.json"
  ISSUE_NODE_ID=$(jq -r '.node_id' "$ISSUE_JSON")
  echo "Node ID: $ISSUE_NODE_ID"

  curl -sSL \
    -H "Accept: application/vnd.github+json" \
    -H "Authorization: Bearer $GITHUB_TOKEN" \
    "$REPO_API/issues/$ISSUE/events" \
    > "$REPO_DIR/issue_events_${ISSUE}.json"

QUERY_JSON=$(cat <<EOF
{
  "query": "query(\$issueId: ID!) { node(id: \$issueId) { ... on Issue { title number projectItems(first: 10) { nodes { fieldValues(first: 10) { nodes { ... on ProjectV2ItemFieldSingleSelectValue { field { name } value } } } } } } } }",
  "variables": {
    "issueId": "$ISSUE_NODE_ID"
  }
}
EOF
)

  # Current error:
  # {"errors":[{"path":["query","node","... on Issue","projectItems","nodes","fieldValues","nodes","... on ProjectV2ItemFieldSingleSelectValue","field","name"],"extensions":{"code":"selectionMismatch","nodeName":"ProjectV2FieldConfiguration"},"locations":[{"line":1,"column":185}],"message":"Selections can't be made directly on unions (see selections on ProjectV2FieldConfiguration)"},{"path":["query","node","... on Issue","projectItems","nodes","fieldValues","nodes","... on ProjectV2ItemFieldSingleSelectValue","value"],"extensions":{"code":"undefinedField","typeName":"ProjectV2ItemFieldSingleSelectValue","fieldName":"value"},"locations":[{"line":1,"column":200}],"message":"Field 'value' doesn't exist on type 'ProjectV2ItemFieldSingleSelectValue'"}]}

  curl -sSL -H "Authorization: Bearer $GITHUB_TOKEN" \
    -H "Accept: application/vnd.github+json" \
    -X POST https://api.github.com/graphql \
    -d "$QUERY_JSON"
    > "$REPO_DIR/issue_metadata_${ISSUE}.json"
done

echo "[$REPO] Data collection complete → $REPO_DIR/"