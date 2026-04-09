def compute_blocker_summary(issues_data: list[dict]) -> dict:
    """
    Uses GitHub's native issue dependency data (issue_dependencies_summary)
    to compute blocker resolution for the sprint.

    total_blocked  — issues that had at least one blocker (total_blocked_by > 0)
    total_resolved — of those, how many are closed/completed
    """
    total_blocked = 0
    total_resolved = 0

    for issue in issues_data:
        deps = issue.get("issue_dependencies_summary", {})
        if deps.get("total_blocked_by", 0) > 0:
            total_blocked += 1
            if issue.get("closed_at"):
                total_resolved += 1

    return {"total_blocked": total_blocked, "total_resolved": total_resolved}
