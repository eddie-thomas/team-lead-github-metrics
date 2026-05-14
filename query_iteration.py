"""GitHub Projects v2 iteration fetcher and metrics reporter."""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

SCRIPT_DIR = Path(__file__).parent
load_dotenv(SCRIPT_DIR / "github.env")

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
_DEFAULT_PROJECT_NUMBER = int(os.environ.get("PROJECT_NUMBER", "82"))
OWNER = "semanticarts"
GRAPHQL_URL = "https://api.github.com/graphql"
API_BASE = f"https://api.github.com/repos/{OWNER}"

console = Console()


def _graphql(query: str) -> dict:
    resp = requests.post(
        GRAPHQL_URL,
        json={"query": query},
        headers={
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Content-Type": "application/json",
        },
    )
    resp.raise_for_status()
    data = resp.json()
    if "errors" in data:
        console.print("[red]GraphQL error:[/red]", data["errors"])
        sys.exit(1)
    return data


def _rest_get(url: str) -> object:
    resp = requests.get(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {GITHUB_TOKEN}",
        },
    )
    resp.raise_for_status()
    return resp.json()


def _save(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(data, f)


def resolve_current_iteration(project_number: int) -> str:
    data = _graphql(f"""
        query {{
          organization(login: "{OWNER}") {{
            projectV2(number: {project_number}) {{
              field(name: "Iteration") {{
                ... on ProjectV2IterationField {{
                  configuration {{
                    iterations {{ id title startDate duration }}
                  }}
                }}
              }}
            }}
          }}
        }}
    """)
    now = time.time()
    iterations = (
        data["data"]["organization"]["projectV2"]["field"]
        ["configuration"]["iterations"]
    )
    for it in iterations:
        start = datetime.strptime(it["startDate"], "%Y-%m-%d").timestamp()
        end = start + it["duration"] * 86400
        if start <= now < end:
            return it["title"]
    console.print("[red]No current iteration found.[/red]")
    sys.exit(1)


def fetch_project_items(project_number: int, progress: Progress, task_id: object) -> list:
    all_nodes: list = []
    cursor: str | None = None
    while True:
        after = f', after: "{cursor}"' if cursor else ""
        data = _graphql(f"""
            query {{
              organization(login: "{OWNER}") {{
                projectV2(number: {project_number}) {{
                  items(first: 100{after}) {{
                    pageInfo {{ hasNextPage endCursor }}
                    nodes {{
                      content {{
                        __typename
                        ... on Issue {{ number title state url repository {{ name }} }}
                        ... on PullRequest {{ number title state url repository {{ name }} }}
                      }}
                      iteration: fieldValueByName(name: "Iteration") {{
                        ... on ProjectV2ItemFieldIterationValue {{ title iterationId }}
                      }}
                      status: fieldValueByName(name: "Status") {{
                        ... on ProjectV2ItemFieldSingleSelectValue {{ name }}
                      }}
                    }}
                  }}
                }}
              }}
            }}
        """)
        page = data["data"]["organization"]["projectV2"]["items"]
        all_nodes.extend(page["nodes"])
        progress.update(task_id, description=f"Querying Projects v2... ({len(all_nodes)} items fetched)")
        if not page["pageInfo"]["hasNextPage"]:
            break
        cursor = page["pageInfo"]["endCursor"]
    return all_nodes


def filter_items(nodes: list, iteration_title: str) -> list:
    items = []
    for node in nodes:
        it = node.get("iteration")
        if not isinstance(it, dict) or it.get("title") != iteration_title:
            continue
        content = node["content"]
        items.append({
            "type": content["__typename"],
            "number": content["number"],
            "title": content["title"],
            "state": content["state"],
            "status": (node.get("status") or {}).get("name", "—"),
            "url": content["url"],
            "repo": content["repository"]["name"],
        })
    return items


def fetch_pr(repo: str, number: int, temp_dir: Path, progress: Progress, task_id: object) -> None:
    repo_dir = temp_dir / repo
    repo_api = f"{API_BASE}/{repo}"
    progress.update(task_id, description=f"Fetching PR #{number} ({repo})...")
    _save(repo_dir / f"pull_{number}.json", _rest_get(f"{repo_api}/pulls/{number}"))
    _save(repo_dir / f"pull_reviews_{number}.json", _rest_get(f"{repo_api}/pulls/{number}/reviews"))


def fetch_issue(repo: str, number: int, temp_dir: Path, progress: Progress, task_id: object) -> None:
    repo_dir = temp_dir / repo
    repo_api = f"{API_BASE}/{repo}"

    progress.update(task_id, description=f"Fetching Issue #{number} ({repo})...")
    _save(repo_dir / f"issue_{number}.json", _rest_get(f"{repo_api}/issues/{number}"))

    timeline = _rest_get(f"{repo_api}/issues/{number}/timeline")
    _save(repo_dir / f"issue_events_{number}.json", timeline)

    progress.update(task_id, description=f"Fetching status transitions for Issue #{number}...")
    transitions = []
    for event in timeline:
        if event.get("event") != "project_v2_item_status_changed":
            continue
        result = _graphql(f"""
            query {{
              node(id: "{event['node_id']}") {{
                ... on ProjectV2ItemStatusChangedEvent {{
                  createdAt previousStatus status
                }}
              }}
            }}
        """)
        transitions.append(result["data"]["node"])
    _save(repo_dir / f"issue_status_transitions_{number}.json", transitions)

    progress.update(task_id, description=f"Fetching PRs connected to Issue #{number}...")
    connected = _graphql(f"""
        query {{
          repository(owner: "{OWNER}", name: "{repo}") {{
            issue(number: {number}) {{
              timelineItems(itemTypes: [CONNECTED_EVENT, CROSS_REFERENCED_EVENT], first: 25) {{
                nodes {{
                  ... on ConnectedEvent {{
                    subject {{
                      ... on PullRequest {{ number repository {{ name }} }}
                    }}
                  }}
                  ... on CrossReferencedEvent {{
                    source {{
                      ... on PullRequest {{ number repository {{ name }} }}
                    }}
                  }}
                }}
              }}
            }}
          }}
        }}
    """)

    pr_entries: list[dict] = []
    seen: set[int] = set()
    for node in connected["data"]["repository"]["issue"]["timelineItems"]["nodes"]:
        pr = node.get("subject") or node.get("source")
        if pr and pr.get("number") and pr["number"] not in seen:
            seen.add(pr["number"])
            pr_entries.append({"number": pr["number"], "repo": pr["repository"]["name"]})
    _save(repo_dir / f"issue_pr_map_{number}.json", pr_entries)

    for entry in pr_entries:
        pr_num, pr_repo = entry["number"], entry["repo"]
        progress.console.print(f"  └─ [PR #{pr_num}] {pr_repo} (connected to Issue #{number})")
        fetch_pr(pr_repo, pr_num, temp_dir, progress, task_id)


def run_report(iteration_title: str, temp_dir: Path, summary: bool) -> None:
    from metrics import (
        create_report,
        generate_summary,
        load_issue_metrics_from_dir,
        load_issue_velocity_from_dir,
        load_pr_metrics_from_dir,
        load_pr_review_metrics_from_dir,
    )
    data = [
        load_issue_metrics_from_dir(str(temp_dir)),
        load_pr_metrics_from_dir(str(temp_dir)),
        load_pr_review_metrics_from_dir(str(temp_dir)),
        load_issue_velocity_from_dir(str(temp_dir)),
    ]
    create_report(data, iteration_title)
    if summary:
        generate_summary(str(temp_dir), iteration_title)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="project_status",
        description=(
            "Fetch all issues and PRs from a GitHub Projects v2 iteration "
            "and generate a metrics report."
        ),
    )
    parser.add_argument(
        "iteration",
        metavar="current|<number>",
        help="Iteration number to query (e.g. current, 24)",
    )
    parser.add_argument(
        "--project",
        type=int,
        default=_DEFAULT_PROJECT_NUMBER,
        metavar="N",
        help=f"GitHub Projects v2 project number (default: {_DEFAULT_PROJECT_NUMBER} from github.env)",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Generate an LLM summary of the iteration after fetching",
    )
    parser.add_argument(
        "--no-fetch",
        action="store_true",
        help="Skip data fetching and use existing cached data",
    )
    args = parser.parse_args()

    if not GITHUB_TOKEN:
        console.print("[red]GITHUB_TOKEN is not set in github.env or environment.[/red]")
        sys.exit(1)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("Starting...", total=None)

        if args.iteration == "current":
            progress.update(task, description="Fetching current iteration...")
            iteration_title = resolve_current_iteration(args.project)
            iteration_num = iteration_title.split()[-1].lstrip("0") or "0"
        else:
            iteration_num = args.iteration
            iteration_title = f"Iteration {iteration_num}"

        temp_dir = SCRIPT_DIR / "temp" / f"iteration_{iteration_num}"

        if args.no_fetch:
            progress.console.print(f"Skipping data fetch → using existing data in [bold]{temp_dir}[/bold]")
        else:
            progress.update(task, description=f"Querying {iteration_title} from Projects v2...")
            all_nodes = fetch_project_items(args.project, progress, task)
            items = filter_items(all_nodes, iteration_title)

            progress.console.print(f"Found [bold]{len(items)}[/bold] items in {iteration_title}\n")

            for item in items:
                number, repo = item["number"], item["repo"]
                if item["type"] == "PullRequest":
                    progress.console.print(f"[PR #{number}] {repo}")
                    fetch_pr(repo, number, temp_dir, progress, task)
                elif item["type"] == "Issue":
                    progress.console.print(f"[Issue #{number}] {repo}")
                    fetch_issue(repo, number, temp_dir, progress, task)

            progress.console.print(f"\nData collection complete → [bold]{temp_dir}/[/bold]\n")

    run_report(iteration_title, temp_dir, args.summary)


if __name__ == "__main__":
    main()
