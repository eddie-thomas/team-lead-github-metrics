# GitHub Metrics Script Setup

This project uses the GitHub API to gather issue and pull request data.
To run the scripts you need a **GitHub Personal Access Token (PAT)**.

---

## Step 1 — Create a GitHub Personal Access Token (PAT)

GitHub supports **fine-grained PATs**, which are scoped to only the permissions you need for this script, making them more secure than classic PATs.

### Official Documentation

- **Managing your personal access tokens (GitHub)**
  Instructions for creating a fine-grained PAT:
  [https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)

- **Setting a personal access token policy (GitHub)**
  Info on approval requirements and organization policies:
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
9. Select the specific repos you need (e.g., `dca`)
10. Under **Permissions**, grant:

- **Issues: Read**
- **Pull requests: Read**
- **Metadata: Read**

> Note: We'll want to add read access for **Project v2**

11. Generate the token and copy it

If your org requires approval for fine-grained PATs, it may show as _pending_ until an admin approves it.

---

## Step 2 — Create your `github.env` file

After the PAT is approved, create a file named `github.env` in the project directory.

**Example content:**

```env
# github.env
GITHUB_TOKEN=github_pat_XXXXXXXXXXXXXXXXXXXXXXXXXXXX
EXPIRED_DATE=1799564400
```

- `GITHUB_TOKEN` — Your PAT string (copy it securely)
- `EXPIRED_DATE` — The Unix timestamp (in seconds) when this token expires

❗ **Do not commit `github.env` to version control.**

---

## Step 3 — Run the script

Once the environment file exists you can run the script:

```bash
./run_metrics.sh --repo dca --issues 1234 --report

# Run the help command for program details
./run_metrics.sh --help
```

The script will:

- Check that the token has not expired
- Perform authenticated requests to GitHub’s API
- Save results to a temporary output directory (`/temp`)
- **Optionally** prints out a complete report of the repository stats (use the `--report` flag to output the report)

---

## Common Errors & Fixes

### `401 Bad credentials`

- Double-check your token value in `github.env` is correctly copied over
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
