import json
from pathlib import Path


def extract_issue_metrics(issue_json: dict) -> dict:
    """
    Extracts key metrics from a GitHub issue JSON.
    """
    metrics = {
        "number": issue_json.get("number"),
        "title": issue_json.get("title"),
        "url": issue_json.get("html_url"),
        "state": issue_json.get("state"),
        "author": issue_json.get("user", {}).get("login"),
        "author_association": issue_json.get("author_association"),
        "assignees": [a.get("login") for a in issue_json.get("assignees", [])],
        "labels": [l.get("name") for l in issue_json.get("labels", [])],
        "comments": issue_json.get("comments"),
        "created_at": issue_json.get("created_at"),
        "updated_at": issue_json.get("updated_at"),
        "closed_at": issue_json.get("closed_at"),
        "body": issue_json.get("body"),
        "sub_issues_summary": issue_json.get("sub_issues_summary", {}),
        "issue_dependencies_summary": issue_json.get("issue_dependencies_summary", {}),
        "reactions": issue_json.get("reactions", {}),
    }
    return metrics


def load_issue_metrics_from_dir(dir_path: str | Path) -> list[dict]:
    dir_path = Path(dir_path)

    print(dir_path.resolve())

    results = []

    for file in sorted(dir_path.rglob("*/issue_*.json")):
        print(f"Pulling data from {file.name}...")
        # Skip review files
        if "events" in file.name:
            continue

        with file.open() as f:
            pr_data = json.load(f)

        results.append(extract_issue_metrics(pr_data))

    return results
