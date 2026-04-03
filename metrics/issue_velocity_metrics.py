import json
from datetime import datetime
from pathlib import Path


STATUS_ORDER = [
    "Triage",
    "Ready To Assign",
    "Todo",
    "In Progress",
    "In Review",
    "Change Requested",
    "Merged",
    "Done",
]

# Statuses that indicate active work has begun
ACTIVE_STATUSES = {"In Progress", "In Review", "Change Requested", "Merged", "Done"}


def parse(ts):
    return datetime.fromisoformat(ts.replace("Z", "+00:00")) if ts else None


def find_start_transition(transitions: list[dict]) -> dict | None:
    """
    Returns the latest transition where status == 'Todo'.
    If none exists, falls back to the earliest transition by STATUS_ORDER rank.
    """
    todo = [t for t in transitions if t.get("status") == "Todo"]
    if todo:
        return max(todo, key=lambda t: t["createdAt"])

    # Fallback: only use transitions that moved into an active status
    active = [t for t in transitions if t.get("status") in ACTIVE_STATUSES]
    if not active:
        return None

    def order_rank(t):
        status = t.get("status", "")
        rank = (
            STATUS_ORDER.index(status) if status in STATUS_ORDER else len(STATUS_ORDER)
        )
        return (rank, t["createdAt"])

    return min(active, key=order_rank)


def extract_issue_velocity(
    issue_number: str, transitions: list[dict], closed_at: str | None
) -> dict | None:
    if not transitions or not closed_at:
        return None

    closed_ts = parse(closed_at)
    start = find_start_transition(transitions)
    if not start:
        return None

    start_ts = parse(start["createdAt"])
    if start_ts >= closed_ts:
        return None

    active_hours = (closed_ts - start_ts).total_seconds() / 3600

    return {
        "issue_number": issue_number,
        "transition_count": len(transitions),
        "start_status": start.get("status"),
        "start_at": start["createdAt"],
        "closed_at": closed_at,
        "total_active_hours": active_hours,
    }


def load_issue_velocity_from_dir(dir_path: str) -> list[dict]:
    dir_path = Path(dir_path)
    results = []

    for file in sorted(dir_path.rglob("*/issue_status_transitions_*.json")):
        issue_number = file.stem.replace("issue_status_transitions_", "")

        issue_file = file.parent / f"issue_{issue_number}.json"
        if not issue_file.exists():
            continue

        with issue_file.open() as f:
            closed_at = json.load(f).get("closed_at")

        with file.open() as f:
            transitions = json.load(f)

        metric = extract_issue_velocity(issue_number, transitions, closed_at)
        if metric:
            results.append(metric)

    return results
