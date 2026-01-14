from metrics import create_report, load_issue_metrics_from_dir, load_pr_metrics_from_dir, load_pr_review_metrics_from_dir


if __name__ == "__main__":
    data = [
        load_issue_metrics_from_dir("./temp/"),
        load_pr_metrics_from_dir("./temp/"),
        load_pr_review_metrics_from_dir("./temp/"),
    ]

    create_report(data)
