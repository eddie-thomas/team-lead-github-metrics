from datetime import datetime
import statistics

# -----------------------------
# Utility functions
# -----------------------------


def parse(ts):
    return datetime.fromisoformat(ts.replace("Z", "+00:00")) if ts else None


def hours_between(start: datetime, end: datetime):
    return (end - start).total_seconds() / 3600


def create_report(data: list[list[dict]], title: str):
    issues_data = data[0]
    prs_data = data[1]
    reviews_data = [item for sublist in data[2] for item in sublist] if data[2] else []
    velocity_data = data[3] if len(data) > 3 else []
    rollover_data = data[4] if len(data) > 4 else []

    # -----------------------------
    # Prepare timestamps
    # -----------------------------
    created = []
    issues_created = []
    first_review = []
    merged_at = []
    done_at = []
    issues_done_at = []

    # --- Issues ---
    for issue in issues_data:
        if not issue.get("created_at"):
            continue

        issues_created.append(parse(issue.get("created_at")))
        issues_done_at.append(parse(issue.get("closed_at")))

    # --- PRs ---
    for pr in prs_data:
        pr_created_at = parse(pr.get("created_at"))
        created.append(pr_created_at)

        # Find first review timestamp for this PR
        pr_reviews = [
            r
            for r in reviews_data
            if r.get("review_url", "").startswith(
                f"https://github.com/{pr['repo']}/pull/{pr['pr_number']}"
            )
        ]
        if pr_reviews:
            first_review_ts = min(
                parse(r["submitted_at"]) for r in pr_reviews if r.get("submitted_at")
            )
            first_review.append(first_review_ts)
        else:
            first_review.append(None)

        merged_at.append(parse(pr.get("merged_at")))
        done_at.append(parse(pr.get("closed_at")))

    # -----------------------------
    # Metrics calculations
    # -----------------------------
    # 1. Median PR/Issue time to first response
    first_response_hours = [
        hours_between(created[i], first_review[i])
        for i in range(len(created))
        if first_review[i]
    ]
    median_first_response = (
        statistics.median(first_response_hours) if first_response_hours else 0
    )
    average_first_response = (
        statistics.mean(first_response_hours) if first_response_hours else 0
    )

    # 2. Median PR time to merge
    merge_hours = [
        (hours_between(created[i], merged_at[i]) / 24)
        for i in range(len(created))
        if merged_at[i]
    ]
    median_merge_time = statistics.median(merge_hours) if merge_hours else 0
    average_merge_time = statistics.mean(merge_hours) if merge_hours else 0

    # 3. Review compliance rate (≤ 24 hours)
    compliant = sum(1 for h in first_response_hours if h <= 24)
    review_compliance_rate = (
        (compliant / len(first_response_hours) * 100) if first_response_hours else 0
    )

    # 4. Issues completed (%)
    total_items = len(issues_created)
    completed_items = sum(1 for d in issues_done_at if d)
    issues_completed_pct = (completed_items / total_items * 100) if total_items else 0

    # -----------------------------
    # Output
    # -----------------------------

    LINE = "─" * 52
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    RESET = "\033[0m"

    def sla_color(green_threshold, yellow_threshold):
        if green_threshold:
            return GREEN
        elif yellow_threshold:
            return YELLOW
        else:
            return RED

    print()
    print(LINE)
    print(title)
    print(LINE)

    median_first_response_width = len(f"{median_first_response:>.2f}")
    print(
        f"{'Median PR time to first response:':42} "
        f"{sla_color(median_first_response <= 24, median_first_response <= 48)}{median_first_response:>{median_first_response_width}.2f} hrs{RESET}"
    )

    average_first_response_width = len(f"{average_first_response:>.2f}")
    print(
        f"{'Average PR time to first response:':42} "
        f"{sla_color(average_first_response <= 24, average_first_response <= 48)}{average_first_response:>{average_first_response_width}.2f} hrs{RESET}"
    )
    print(f"{'Target (first response):':42} {'≤ 24':>4} hrs")
    print()

    median_merge_time_width = len(f"{median_merge_time:>.0f}")
    print(
        f"{'Median PR time to merge:':42} {median_merge_time:>{median_merge_time_width}.0f} days"
    )
    average_merge_time_width = len(f"{review_compliance_rate:>.0f}")
    print(
        f"{'Average PR time to merge:':42} {average_merge_time:>{average_merge_time_width}.0f} days"
    )
    print()

    review_compliance_rate_width = len(f"{review_compliance_rate:>.1f}")
    print(
        f"{'Review compliance (≤ 24h):':42} "
        f"{GREEN if review_compliance_rate >= 90 else YELLOW}"
        f"{review_compliance_rate:>{review_compliance_rate_width}.1f}%{RESET}"
    )
    print()

    # Per-reviewer first response breakdown
    reviewer_hours: dict[str, list[float]] = {}
    for pr in prs_data:
        pr_created_at = parse(pr.get("created_at"))
        if not pr_created_at:
            continue
        pr_prefix = f"https://github.com/{pr['repo']}/pull/{pr['pr_number']}"
        pr_reviews = [
            r for r in reviews_data if r.get("review_url", "").startswith(pr_prefix)
        ]

        # Collect each reviewer's first review on this PR
        by_reviewer: dict[str, list] = {}
        for r in pr_reviews:
            if r.get("submitted_at"):
                by_reviewer.setdefault(r["reviewer"], []).append(
                    parse(r["submitted_at"])
                )
        for reviewer, timestamps in by_reviewer.items():
            first_ts = min(timestamps)
            reviewer_hours.setdefault(reviewer, []).append(
                hours_between(pr_created_at, first_ts)
            )

    if reviewer_hours:
        print(f"  {'Reviewer':<24} {'Median':>8}   {'Avg':>8}   {'Reviews':>7}")
        print(f"  {'─' * 24} {'─' * 8}   {'─' * 8}   {'─' * 7}")
        for reviewer, hours in sorted(reviewer_hours.items()):
            med = statistics.median(hours)
            avg = statistics.mean(hours)
            color = sla_color(med <= 24, med <= 48)
            print(
                f"  {reviewer:<24} {color}{med:>7.1f}h{RESET}   {color}{avg:>7.1f}h{RESET}   {len(hours):>7}"
            )
        print()

    issues_completed_pct_width = len(f"{issues_completed_pct:>.1f}")
    print(
        f"{'Issues completed this sprint:':42} "
        f"{completed_items}/{total_items} ({sla_color(issues_completed_pct > 90, issues_completed_pct > 80)}{issues_completed_pct:{issues_completed_pct_width}.1f}%{RESET})"
    )
    print()

    blocker_pct = 0
    blocker_pct_width = len(f"{blocker_pct:>.1f}")
    print(
        f"{'Blockers resolved within 48 hrs:':42} "
        f"{0}/{0} ({sla_color(blocker_pct == 0, 0 > 0.8)}{blocker_pct:{blocker_pct_width}.1f}%{RESET})"
    )

    print(LINE)
    print()

    # -----------------------------
    # Issue velocity
    # -----------------------------
    if velocity_data:
        all_transitions = [v["transition_count"] for v in velocity_data]
        all_active_hours = [v["total_active_hours"] for v in velocity_data]
        avg_transitions = statistics.mean(all_transitions)
        avg_active_hours = statistics.mean(all_active_hours)

        # Flag issues that were active longer than a single sprint (14 days)
        LONG_RUNNING_THRESHOLD_DAYS = 14
        churned = [
            v
            for v in velocity_data
            if v["total_active_hours"] / 24 > LONG_RUNNING_THRESHOLD_DAYS
        ]

        print("Issue Velocity")
        print(LINE)
        print(f"{'Issues tracked (with transitions):':42} {len(velocity_data)}")
        print(f"{'Avg status transitions per issue:':42} {avg_transitions:.1f}")
        print(
            f"{'Avg time first → last transition:':42} {avg_active_hours / 24:.1f} days"
        )
        print()

        print(f"  {'Issue':<10} {'Transitions':>12}   {'Active (days)':>13}")
        print(f"  {'─' * 10} {'─' * 12}   {'─' * 13}")
        for v in sorted(
            velocity_data, key=lambda x: x["total_active_hours"], reverse=True
        ):
            sprints_over = v["total_active_hours"] / 24 / LONG_RUNNING_THRESHOLD_DAYS
            long_flag = (
                f" {YELLOW}({int(sprints_over)} sprint(s) overdue){RESET}"
                if v["total_active_hours"] / 24 > LONG_RUNNING_THRESHOLD_DAYS
                else ""
            )
            print(
                f"  #{v['issue_number']:<9} {v['transition_count']:>12}   {v['total_active_hours'] / 24:>12.1f}d{long_flag}"
            )
        print()

        if churned:
            print(
                f"  {YELLOW}{len(churned)} issue(s) were active longer than the sprint ({LONG_RUNNING_THRESHOLD_DAYS} days){RESET}"
            )
            print()

        print(LINE)
        print()

    # -----------------------------
    # Iteration rollovers
    # -----------------------------
    if rollover_data:
        print("Iteration Rollovers")
        print(LINE)
        print(f"  {'Issue':<12} {'Repo':<20} {'Rollovers':>9}   Iterations")
        print(f"  {'─' * 12} {'─' * 20} {'─' * 9}   {'─' * 20}")
        for r in rollover_data:
            iters = " → ".join(str(i) for i in r["iterations"])
            flag = (
                f" {YELLOW}⚑ {r['rollover_count']} rollover(s){RESET}"
                if r["rollover_count"] > 1
                else ""
            )
            print(
                f"  #{r['issue_number']:<11} {r['repo']:<20} {r['rollover_count']:>9}   {iters}{flag}"
            )
        multi = sum(1 for r in rollover_data if r["rollover_count"] > 1)
        print()
        print(
            f"  {len(rollover_data)} issue(s) carried over from a previous iteration",
            end="",
        )
        if multi:
            print(f", {YELLOW}{multi} carried over more than once{RESET}", end="")
        print()
        print(LINE)
        print()
