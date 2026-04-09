import json
import urllib.request
from pathlib import Path


OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "qwen2.5:7b"


def _load_json(path: Path) -> dict | list | None:
    if not path.exists():
        return None
    with path.open() as f:
        return json.load(f)


def build_issue_context(data_dir: str) -> list[dict]:
    base = Path(data_dir)
    issues = []

    for issue_file in sorted(base.rglob("*/issue_[0-9]*.json")):
        if "events" in issue_file.name or "transitions" in issue_file.name:
            continue

        issue = _load_json(issue_file)
        if not issue or issue.get("state_reason") != "completed":
            continue

        number = issue.get("number")
        repo_dir = issue_file.parent

        pr_map = _load_json(repo_dir / f"issue_pr_map_{number}.json") or []
        prs = []
        for entry in pr_map:
            pr_file = base / entry["repo"] / f"pull_{entry['number']}.json"
            pr = _load_json(pr_file)
            if pr:
                prs.append(
                    {
                        "number": pr.get("number"),
                        "title": pr.get("title"),
                        "body": (pr.get("body") or "").strip(),
                        "state": pr.get("state"),
                        "merged": pr.get("merged_at") is not None,
                        "url": pr.get("html_url"),
                    }
                )

        issues.append(
            {
                "number": number,
                "title": issue.get("title"),
                "body": (issue.get("body") or "").strip(),
                "state": issue.get("state"),
                "url": issue.get("html_url"),
                "assignees": [a.get("login") for a in issue.get("assignees", [])],
                "prs": prs,
            }
        )

    return issues


def build_issue_prompt(issue: dict) -> str:
    lines = [
        "You are writing sprint release notes for a C-suite audience.",
        "Your job is to write one punchy, specific bullet point per work item.",
        "",
        "Rules:",
        "- The top-level bullet MUST name the specific feature, system, or workflow affected — not a generic description.",
        "- Do NOT start with 'Improved', 'Enhanced', 'Updated', 'Fixed', or 'Streamlined'.",
        "- Vary your sentence structure. Lead with the outcome, the user, or the thing that changed.",
        "- Be specific. 'Pay rate changes now take effect automatically' beats 'Improved payroll management'.",
        "- Follow with 2-4 indented sub-bullets that add concrete detail or context.",
        "- No markdown headers. No preamble. No closing remarks. Just the bullets.",
        "",
        "Format:",
        "• <specific, punchy one-sentence summary that names the thing>",
        "  - <concrete detail>",
        "  - <concrete detail>",
        "",
        "WORK ITEM:",
        f"Title: {issue['title']}",
    ]

    if issue["assignees"]:
        lines.append(f"Assigned to: {', '.join(issue['assignees'])}")

    if issue["body"]:
        lines.append(f"Description: {issue['body'][:800]}")

    if issue["prs"]:
        lines.append("Delivered via:")
        for pr in issue["prs"]:
            status = "Merged" if pr["merged"] else pr["state"].capitalize()
            lines.append(f"  - PR #{pr['number']} ({status}): {pr['title']}")
            if pr["body"]:
                lines.append(f"    {pr['body'][:400]}")

    return "\n".join(lines)


def call_ollama_with_messages(messages: list[dict]) -> str:
    payload = json.dumps(
        {
            "model": OLLAMA_MODEL,
            "messages": messages,
            "stream": False,
        }
    ).encode()

    req = urllib.request.Request(
        OLLAMA_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=120) as resp:
        result = json.loads(resp.read())
        return result["message"]["content"].strip()


def call_ollama(prompt: str) -> str:
    payload = json.dumps(
        {
            "model": OLLAMA_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
        }
    ).encode()

    req = urllib.request.Request(
        OLLAMA_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=120) as resp:
        result = json.loads(resp.read())
        return result["message"]["content"].strip()


def generate_summary(data_dir: str, title: str):
    issues = build_issue_context(data_dir)

    if not issues:
        print("No issues found — skipping summary.")
        return

    LINE = "─" * 52
    print()
    print(LINE)
    print(f"Executive Summary — {title}")
    print(LINE)
    print()

    safe_title = title.replace(" ", "_").replace("|", "").replace("/", "-").strip("_")
    md_file = Path(data_dir) / f"{safe_title}.md"
    html_file = Path(data_dir) / f"{safe_title}.html"

    md_lines = [f"# Executive Summary — {title}", ""]
    html_items = []
    issue_summaries = []

    for i, issue in enumerate(issues, 1):
        print(f"[{i}/{len(issues)}] Summarizing Issue #{issue['number']}...", end="\r")
        issue_prompt = build_issue_prompt(issue)
        response = call_ollama(issue_prompt)
        issue_summaries.append((issue_prompt, response))

        # Build link collections
        md_links = []
        html_links = []
        if issue.get("url"):
            md_links.append(f"[Issue #{issue['number']}]({issue['url']})")
            html_links.append(f'<a href="{issue["url"]}">Issue #{issue["number"]}</a>')
        for pr in issue["prs"]:
            if pr.get("url"):
                md_links.append(f"[PR #{pr['number']}]({pr['url']})")
                html_links.append(f'<a href="{pr["url"]}">PR #{pr["number"]}</a>')

        md_link_str = "  " + " · ".join(md_links) if md_links else ""
        html_link_str = " &nbsp;·&nbsp; ".join(html_links) if html_links else ""

        lines = response.splitlines()
        top = lines[0] if lines else ""
        subs = [l for l in lines[1:] if l.strip()]

        # Fail-safe: warn if any non-empty lines from the response were dropped
        expected = sum(1 for l in lines[1:] if l.strip())
        if len(subs) != expected:
            raise ValueError(
                f"\033[K  [!] Issue #{issue['number']}: expected {expected} sub-bullets, captured {len(subs)}"
            )

        # Markdown output
        # Before first •: - lines are single indent
        # After first •: - lines are double indent (detail under secondary bullet)
        md_top = top + md_link_str
        md_subs = []
        seen_secondary = False
        for s in subs:
            if s.lstrip().startswith("•"):
                seen_secondary = True
                md_subs.append(f"  - {s.lstrip('• ').strip()}")
            else:
                indent = "    - " if seen_secondary else "  - "
                md_subs.append(f"{indent}{s.lstrip('- ').strip()}")
        formatted_md = "\n".join([md_top] + md_subs)
        print(f"\033[K{formatted_md}")
        print()
        md_lines.append(formatted_md)
        md_lines.append("")

        # HTML list item
        # Before first •: - lines are normal <li>
        # After first •: - lines are nested <ul><li> (detail)
        sub_html_parts = []
        seen_secondary = False
        for s in subs:
            if s.lstrip().startswith("•"):
                seen_secondary = True
                sub_html_parts.append(
                    f"<li><strong>{s.lstrip('• ').strip()}</strong></li>"
                )
            elif seen_secondary:
                sub_html_parts.append(
                    f"<ul><li style='color:#555;'>{s.lstrip('- ').strip()}</li></ul>"
                )
            else:
                sub_html_parts.append(f"<li>{s.lstrip('- ').strip()}</li>")
        sub_html = "".join(sub_html_parts)

        html_items.append(
            f"<li>{top.lstrip('• ').strip()} "
            f'<span style="font-size:0.85em; color:#555;">{html_link_str}</span>'
            f"<ul>{sub_html}</ul></li>"
        )

    # Call Ollama once more, but with every prompt and every response, so it has full context of the summary
    # and can summarize the most important points across all issues.
    print(f"\033[KGenerating sprint highlights...", end="\r")
    highlight_prompt = (
        "You have just reviewed every work item completed this sprint. "
        "Your task is to select and rank the 3–6 most business-significant items for a C-suite audience. "
        "Be ruthlessly selective. Most items will not make this list.\n\n"
        "Prioritize items in this order:\n"
        "1. Revenue or financial impact (pricing changes, commission rates, billing logic, payroll accuracy)\n"
        "2. Compliance, legal, or audit risk (anything that was broken and could create liability)\n"
        "3. Significant user-facing capability added or restored\n"
        "4. Workflow or process changes that save meaningful time or eliminate manual work\n\n"
        "Do NOT include: minor bug fixes with no financial or user impact, internal refactors, small UI tweaks, "
        "configuration file changes, or anything a non-technical stakeholder would not care about. "
        "If something sounds like 'minor fix' or 'small update', leave it out.\n\n"
        "Each bullet must name the specific thing that changed and why it matters to the business — not how it was built. "
        "Do not repeat detail from the full summary — distill it. "
        "No headers, no preamble, no closing remarks. Just the bullets.\n\n"
        "Format:\n• <outcome-first sentence naming the specific thing and its business impact>"
    )
    chained_messages = []
    for issue_prompt, issue_response in issue_summaries:
        chained_messages.append({"role": "user", "content": issue_prompt})
        chained_messages.append({"role": "assistant", "content": issue_response})
    chained_messages.append({"role": "user", "content": highlight_prompt})
    highlights = call_ollama_with_messages(chained_messages)

    print(f"\033[K")
    print("Sprint Highlights")
    print(highlights)
    print()
    md_lines.insert(1, f"## Sprint Highlights\n\n{highlights}\n\n---")
    html_highlights = "".join(
        f"<li><strong>{line.lstrip('• ').strip()}</strong></li>"
        for line in highlights.splitlines()
        if line.strip().startswith("•")
    )

    print(LINE)
    print()

    with md_file.open("w") as f:
        f.write("\n".join(md_lines))
    print(f"Markdown written to {md_file}")

    html_body = "\n".join(html_items)
    html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ font-family: Arial, sans-serif; font-size: 14px; line-height: 1.6; max-width: 800px; margin: 40px auto; color: #222; }}
  h1 {{ font-size: 18px; margin-bottom: 16px; }}
  ul {{ padding-left: 20px; }}
  li {{ margin-bottom: 10px; }}
  li ul {{ margin-top: 4px; }}
  li ul li {{ margin-bottom: 2px; color: #444; }}
  a {{ color: #0066cc; text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
</style>
</head>
<body>
<h1>Executive Summary — {title}</h1>
<h2 style="font-size:15px; margin-top:20px;">Sprint Highlights</h2>
<ul>
{html_highlights}
</ul>
<hr style="margin: 24px 0;">
<ul>
{html_body}
</ul>
</body>
</html>"""

    with html_file.open("w") as f:
        f.write(html_content)
    print(f"HTML written to {html_file}")
