import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any


def parse_github_ts(ts: Optional[str]) -> Optional[datetime]:
    """Parse GitHub ISO timestamps safely."""
    if not ts:
        return None
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def hours_between(start: datetime, end: datetime) -> float:
    return (end - start).total_seconds() / 3600


def extract_pr_metrics(pr_json: Dict[str, Any]) -> Dict[str, Any]:
    now = datetime.now(timezone.utc)

    created_at = parse_github_ts(pr_json.get("created_at"))
    updated_at = parse_github_ts(pr_json.get("updated_at"))
    closed_at = parse_github_ts(pr_json.get("closed_at"))
    merged_at = parse_github_ts(pr_json.get("merged_at"))

    metrics = {
        # Identity
        "pr_number": pr_json["number"],
        "title": pr_json["title"],
        "repo": pr_json["base"]["repo"]["full_name"],
        "author": pr_json["user"]["login"],
        "author_association": pr_json.get("author_association"),

        # State
        "state": pr_json["state"],
        "draft": pr_json["draft"],
        "merged": pr_json["merged"],
        "mergeable": pr_json.get("mergeable"),
        "mergeable_state": pr_json.get("mergeable_state"),

        # Timestamps
        "created_at": created_at,
        "updated_at": updated_at,
        "closed_at": closed_at,
        "merged_at": merged_at,

        # Durations (hours)
        "hours_open": hours_between(created_at, merged_at or now)
            if created_at else None,

        "hours_to_merge": hours_between(created_at, merged_at)
            if created_at and merged_at else None,

        # Review posture
        "requested_reviewers": [
            r["login"] for r in pr_json.get("requested_reviewers", [])
        ],
        "requested_reviewers_count": len(
            pr_json.get("requested_reviewers", [])
        ),

        # Activity / size
        "comments_count": pr_json.get("comments", 0),
        "review_comments_count": pr_json.get("review_comments", 0),
        "commits_count": pr_json.get("commits", 0),
        "additions": pr_json.get("additions", 0),
        "deletions": pr_json.get("deletions", 0),
        "changed_files": pr_json.get("changed_files", 0),

        # Labels
        "labels": [label["name"] for label in pr_json.get("labels", [])],
    }

    return metrics


def load_pr_metrics_from_dir(dir_path: str | Path) -> list[dict]:
    dir_path = Path(dir_path)

    print(dir_path.resolve())

    results = []

    for file in sorted(dir_path.rglob("*/pull_*.json")):
        print(f"Pulling data from {file.name}...")
        # Skip review files
        if "reviews" in file.name:
            continue

        with file.open() as f:
            pr_data = json.load(f)

        results.append(extract_pr_metrics(pr_data))

    return results
