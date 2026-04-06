from pathlib import Path


def load_rollover_metrics_from_dir(data_dir: str) -> list[dict]:
    data_path = Path(data_dir)
    temp_root = data_path.parent

    try:
        current_iter = int(data_path.name.split("_")[1])
    except (IndexError, ValueError):
        return []

    iter_issues: dict[int, set[tuple[str, int]]] = {}
    for iter_dir in temp_root.glob("iteration_*"):
        try:
            iter_num = int(iter_dir.name.split("_")[1])
        except (IndexError, ValueError):
            continue
        issues = set()
        for file in iter_dir.rglob("*/issue_*.json"):
            if any(s in file.name for s in ("events", "transitions", "pr_map")):
                continue
            try:
                issue_num = int(file.stem.split("_")[1])
            except (IndexError, ValueError):
                continue
            repo = file.parent.name
            issues.add((repo, issue_num))
        iter_issues[iter_num] = issues

    current_issues = iter_issues.get(current_iter, set())
    results = []
    for repo, issue_num in current_issues:
        appeared_in = sorted(
            n for n, issues in iter_issues.items() if (repo, issue_num) in issues
        )
        if len(appeared_in) > 1:
            results.append(
                {
                    "issue_number": issue_num,
                    "repo": repo,
                    "iterations": appeared_in,
                    "rollover_count": len(appeared_in) - 1,
                }
            )

    return sorted(results, key=lambda x: x["rollover_count"], reverse=True)
