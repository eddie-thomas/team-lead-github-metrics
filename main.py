import sys
from metrics import (
    create_report,
    generate_summary,
    load_issue_metrics_from_dir,
    load_issue_velocity_from_dir,
    load_pr_metrics_from_dir,
    load_pr_review_metrics_from_dir,
)


if __name__ == "__main__":
    title = sys.argv[1] if len(sys.argv) > 1 else "Weekly Engineering Flow Metrics"
    data_dir = sys.argv[2] if len(sys.argv) > 2 else "./temp/"
    summary = "--summary" in sys.argv

    data = [
        load_issue_metrics_from_dir(data_dir),
        load_pr_metrics_from_dir(data_dir),
        load_pr_review_metrics_from_dir(data_dir),
        load_issue_velocity_from_dir(data_dir),
    ]

    create_report(data, title)

    if summary:
        generate_summary(data_dir, title)
