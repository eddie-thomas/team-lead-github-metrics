import json
from pathlib import Path

def extract_pr_review_metrics(reviews: list[dict]):
    """
    Reads a JSON file with GitHub PR review data and extracts key metrics.
    Returns a list of dicts with relevant info.
    """

    metrics = []
    for review in reviews:
        if "codeant-ai[bot]" == review.get("user", {}).get("login"):
            continue
        if "OWNER" == review.get("author_association"):
            continue

        metrics.append({
            "reviewer": review.get("user", {}).get("login"),
            "state": review.get("state"),
            "submitted_at": review.get("submitted_at"),
            "review_url": review.get("html_url"),
            "commit_id": review.get("commit_id"),
            "author_association": review.get("author_association"),
        })

    return metrics

def load_pr_review_metrics_from_dir(dir_path: str | Path) -> list[dict]:
    dir_path = Path(dir_path)

    print(dir_path.resolve())

    results = []

    for file in sorted(dir_path.rglob("*/*_reviews_*.json")):
        with file.open() as f:
            reviews = json.load(f)

        results.append(extract_pr_review_metrics(reviews))

    return results
