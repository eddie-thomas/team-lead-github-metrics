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
# Helper functions
# -------------------------
SPINNER_FRAMES=( '\' '|' '/' '-' )
SPINNER_DELAY=0.1
SPINNER_PID=""

print_help() {
  printf "\nUsage: %s [OPTIONS] [ARGS]\n\n" "$(basename "$0")"
  printf "Options:\n"
  printf "  %-20s %s\n" "--repo REPO" "Specify a single repository to operate on."
  printf "  %-20s %s\n" "--prs PR1 PR2 ..." "Specify one or more pull requests to fetch/analyze."
  printf "  %-20s %s\n" "--issues ISSUE1 ..." "Specify one or more issues to fetch/analyze."
  printf "  %-20s %s\n" "--report" "Generate a report after processing the specified PRs and/or issues. Can be used alone."
  printf "  %-20s %s\n" "-h, --help" "Display this help message and exit."
  printf "\nExamples:\n"
  printf "  %s --report\n" "$(basename "$0")"
  printf "  %s --repo dca --prs 4358 --report\n" "$(basename "$0")"
  printf "  %s --repo quickbooks --prs 4359 4360 --issues 4126 4134\n" "$(basename "$0")"
  printf "  %s --repo dca --issues 4126 4134\n" "$(basename "$0")"
  printf "  %s \ \n%-4s--repo dca \ \n%-4s--prs 4358 \ \n%-4s--issues 4126 4134 \ \n%-4s--report\n\n" "$(basename "$0")"
}


start_spinner() {
  local msg="$1"
  (
    i=0
    tput civis  # hide cursor
    while true; do
      printf "\r%c %s" "${SPINNER_FRAMES[i]}" "$msg"
      i=$(( (i + 1) % ${#SPINNER_FRAMES[@]} ))
      sleep "$SPINNER_DELAY"
    done
  ) &
  SPINNER_PID=$!
}

stop_spinner() {
  if [[ -n "${SPINNER_PID:-}" ]]; then
    # Only try to kill if it still exists
    if kill -0 "$SPINNER_PID" 2>/dev/null; then
      kill "$SPINNER_PID" 2>/dev/null || true
      wait "$SPINNER_PID" 2>/dev/null || true
    fi

    SPINNER_PID=""
    printf "\r\033[K"   # clear line
    tput cnorm          # restore cursor
  fi
}

# Ensure cleanup on exit
trap stop_spinner EXIT INT TERM


# -------------------------
# Argument parsing
# -------------------------
for arg in "$@"; do
  case "$arg" in
    --help|-h)
      print_help
      exit 0
      ;;
    --repo)
      MODE="repo"
      ;;
    --prs)
      MODE="prs"
      ;;
    --issues)
      MODE="issues"
      ;;
    --report)
      MODE="report"
      REPORT=true
      ;;
    --*|-*)  # Catch-all for unknown flags
      echo "Unknown option: $arg"
      print_help
      exit 1
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
        report)
          REPORT=true
          ;;
      esac
      ;;
  esac
done

if [[ -z "${REPO:-}" ]]; then
  if [[ "${REPORT:-}" == "true" ]]; then
    clear
    source .venv/bin/activate
    python main.py
    exit 0
  fi
  echo "--repo is required (e.g. dca, QuickBooks)"
  exit 1
fi

REPO_DIR="$TEMP_DIR/$REPO"
mkdir -p "$TEMP_DIR/$REPO"

REPO_API="$API_BASE/$REPO"

start_spinner "Fetching GitHub PRs..."

# -------------------------
# Fetch PR data
# -------------------------
for PR in "${PRS[@]:-}"; do
  printf "\r\033[K[$REPO] Fetching PR $PR\n"

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

stop_spinner
start_spinner "Fetching GitHub Issues..."

# -------------------------
# Fetch Issue data
# -------------------------
for ISSUE in "${ISSUES[@]:-}"; do
  printf "\r\033[K[$REPO] Fetching Issue $ISSUE\n"

  curl -sSL \
    -H "Accept: application/vnd.github+json" \
    -H "Authorization: Bearer $GITHUB_TOKEN" \
    "$REPO_API/issues/$ISSUE" \
    > "$REPO_DIR/issue_${ISSUE}.json"

  curl -sSL \
    -H "Accept: application/vnd.github+json" \
    -H "Authorization: Bearer $GITHUB_TOKEN" \
    "$REPO_API/issues/$ISSUE/timeline" \
    > "$REPO_DIR/issue_events_${ISSUE}.json"

  # Currently the following curl will grab the issues Project info, but my PAT doesn't
  # have the correct read accessibility. Until I update the PAT appropriately, I won't
  # be able to automate the pulling of issue status labels on the scrum board

  # curl -X POST https://api.github.com/graphql \
  #   -H "Authorization: Bearer $GITHUB_TOKEN" \
  #   -H "Content-Type: application/json" \
  #   -d '{
  #     "query": "query ($issue: Int!) { repository(owner: \"semanticarts\", name: \"dca\") { issue(number: $issue) { title state projectItems(first: 10) { nodes { id project { title } fieldValueByName(name: \"Status\") { __typename ... on ProjectV2ItemFieldSingleSelectValue { name } } } } } } }",
  #     "variables": { "issue": '"$ISSUE"' }
  #   }' \
  #   > "$REPO_DIR/issue_status_${ISSUE}.json"
done

stop_spinner

printf "\r\033[K[$REPO] Data collection complete → $REPO_DIR/\n\n"

if [[ "${REPORT:-}" == "true" ]]; then
  clear
  source .venv/bin/activate
  python main.py
fi
