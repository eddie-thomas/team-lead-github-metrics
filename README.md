# GitHub Metrics

This project uses the GitHub API to gather issue and pull request data from a GitHub Projects v2 board and generate a metrics report.
To run the tool you need a **GitHub Personal Access Token (PAT)**.

---

## Step 1 — Create a GitHub Personal Access Token (PAT)

GitHub supports **fine-grained PATs**, which are scoped to only the permissions you need, making them more secure than classic PATs.

### Official Documentation

- **Managing your personal access tokens (GitHub)**
  [https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)

- **Setting a personal access token policy (GitHub)**
  [https://docs.github.com/organizations/managing-programmatic-access-to-your-organization/setting-a-personal-access-token-policy-for-your-organization](https://docs.github.com/organizations/managing-programmatic-access-to-your-organization/setting-a-personal-access-token-policy-for-your-organization)

### Steps to create a fine-grained PAT

1. Log in to GitHub
2. Click your profile picture → **Settings**
3. In the left sidebar → **Developer settings**
4. Click **Personal access tokens → Fine-grained tokens**
5. Click **Generate new token**
6. Give it a name and set an expiration
7. Choose your organization as the **Resource owner**
8. Pick **Repository access → Only select repositories**
9. Select the specific repos you need
10. Under **Permissions**, grant:

    - **Issues: Read**
    - **Pull requests: Read**
    - **Metadata: Read**

11. Switch to the **Organization** tab under **Permissions** and grant:

    - **Projects: Read**

12. Generate the token and copy it

If your org requires approval for fine-grained PATs, it may show as _pending_ until an admin approves it.

---

## Step 2 — Create your `./github.env` file

Create a file named `github.env` in the project root directory:

```env
# github.env
GITHUB_TOKEN=github_pat_XXXXXXXXXXXXXXXXXXXXXXXXXXXX
EXPIRED_DATE=1799564400
PROJECT_NUMBER=97
WEEK_START_DAY=monday
```

| Setting | Description |
|---|---|
| `GITHUB_TOKEN` | Your PAT string |
| `EXPIRED_DATE` | Unix timestamp when this token expires |
| `PROJECT_NUMBER` | GitHub Projects v2 project number (overridable with `--project`) |
| `WEEK_START_DAY` | First day of the week for `--week` mode (overridable with `--week-start`) |

❗ **Do not commit `github.env` to version control.**

---

## Step 3 — Install

Create a Python virtual environment and install the package:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

This registers the `project_status` command inside the virtual environment.

Note: the `--summary` flag uses [Ollama](https://ollama.com) to generate LLM-powered summaries. Make sure Ollama is installed and running locally before using it.

---

## Step 4 — Run

Activate the virtual environment first:

```bash
source .venv/bin/activate
```

### Iteration mode (default)

Fetches all issues and PRs tagged with a given iteration on the GitHub Projects v2 board:

```bash
# Current active iteration
project_status current

# Specific iteration number
project_status 24

# Skip re-fetching and re-run the report from cached data
project_status 24 --no-fetch

# Generate an LLM-powered executive summary (requires Ollama)
project_status 24 --summary

# Use a different project board
project_status 24 --project 42
```

### Week mode

Uses calendar weeks as the time window instead of iteration tags. Items are included if they were created or closed/merged during the target week.

```bash
# Current calendar week (week start from github.env, default: monday)
project_status current --week

# One week ago
project_status 1 --week

# Three weeks ago, week starting on Friday
project_status 3 --week --week-start friday
```

The tool prints the date range before fetching, e.g.:

```
Date range: 2026-05-11 (Monday) → 2026-05-17 (Sunday)
```

### All options

```
usage: project_status [-h] [--week] [--week-start DAY] [--project N]
                      [--summary] [--no-fetch] [--consider-epics]
                      current|<number>

positional arguments:
  current|<number>     Iteration mode: iteration number or 'current'.
                       Week mode (--week): weeks back from current, or 'current'.

options:
  --week               Use calendar weeks instead of iteration tags
  --week-start DAY     First day of the week (e.g. monday, friday)
  --project N          GitHub Projects v2 project number
  --summary            Generate an LLM executive summary after fetching
  --no-fetch           Skip fetching and use existing cached data
  --consider-epics     Include EPIC: issues in analysis (excluded by default)
```

### What the report includes

- Median and average PR time to first review (SLA target: ≤ 24 hrs)
- Median and average PR time to merge
- Review compliance rate — % of PRs reviewed within 24 hours
- Per-reviewer breakdown (median, average, and review count)
- Issues completed (count and %)
- Issue velocity — status transition counts and active days per issue, with flags for long-running items (> 14 days)

Issues with titles starting with `EPIC:` are excluded from all analysis by default. Pass `--consider-epics` to include them.

### What `--summary` outputs

An LLM-generated executive summary (using `qwen2.5:7b` via Ollama) with one punchy bullet per issue and 2–4 concrete sub-bullets. Results are printed to the terminal and saved as:

- `<title>.md` — Markdown file in the temp data directory
- `<title>.html` — Styled HTML file ready to share

---

## Common Errors & Fixes

### `401 Bad credentials`

- Double-check the token value in `github.env`
- Ensure the PAT is approved and active
- Verify repository access and granted permissions

### Token expired

- If the current timestamp ≥ `EXPIRED_DATE`, regenerate the PAT and update `github.env`

---

## Security Best Practices

- Keep your PAT secret — treat it like a password
- Rotate tokens regularly before they expire

For more general GitHub authentication guidance, see:
[https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
