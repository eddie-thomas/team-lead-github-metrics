from datetime import datetime, timedelta
import json
import statistics
from metrics import load_issue_metrics_from_dir


if __name__ == "__main__":
    print(json.dumps(load_issue_metrics_from_dir("./temp/")))

# -----------------------------
# Helpers
# -----------------------------

# def parse(ts):
#     return datetime.fromisoformat(ts.replace("Z", "+00:00")) if ts else None

# def hours_between(start, end):
#     return (end - start).total_seconds() / 3600

# # Parse timestamps
# created = [parse(t) for t in in_progress]
# first_review = [parse(t) for t in in_review]
# merged_at = [parse(t) for t in merged]
# done_at = [parse(t) for t in done]

# # -----------------------------
# # Metrics
# # -----------------------------

# # 1. Median PR time to first response
# first_response_hours = [
#     hours_between(created[i], first_review[i])
#     for i in range(len(created))
#     if first_review[i]
# ]
# median_first_response = statistics.median(first_response_hours)

# # 2. Median PR time to merge
# merge_hours = [
#     hours_between(created[i], merged_at[i])
#     for i in range(len(created))
#     if merged_at[i]
# ]
# median_merge_time = statistics.median(merge_hours)

# # 3. Review compliance rate (≤ 24 hours)
# compliant = sum(1 for h in first_response_hours if h <= 24)
# review_compliance_rate = compliant / len(first_response_hours) * 100

# # 4. Issues completed per week (%)
# total_prs = len(created)
# completed_prs = sum(1 for d in done_at if d)
# issues_completed_pct = completed_prs / total_prs * 100

# # 5. Average PR time to done (production)
# done_hours = [
#     hours_between(created[i], done_at[i])
#     for i in range(len(created))
#     if done_at[i]
# ]
# avg_time_to_done = statistics.mean(done_hours)

# # -----------------------------
# # Output
# # -----------------------------

# print("\n=== Weekly Engineering Flow Metrics ===\n")

# print(f"Median PR time to first response: {median_first_response:.2f} hours")
# print("Target: ≤ 24 hours\n")

# print(f"Median PR time to merge: {median_merge_time:.2f} hours\n")

# print(f"Review compliance rate (≤ 24h): {review_compliance_rate:.1f}%\n")

# print(f"Issues completed this week: {completed_prs}/{total_prs} "
#       f"({issues_completed_pct:.1f}%)\n")

# print(f"Average PR time to production: {avg_time_to_done:.2f} hours\n")

# print("Blockers resolved within 48h: NOT TRACKED")
# print("Reason: blockers are not explicitly represented in this dataset\n")
