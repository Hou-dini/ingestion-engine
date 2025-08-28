# Ingestion Engine

This repository contains a small data ingestion engine for pulling content from various online sources.

.env
----
Create a `.env` file in the project root with the following values (already provided with placeholders):

- REDDIT_CLIENT_ID
- REDDIT_CLIENT_SECRET
- REDDIT_USER_AGENT
- YOUTUBE_API_KEY
- GCS_BUCKET_NAME
- GCS_CREDENTIALS_JSON
- ENV (e.g., development)

Security best practices
-----------------------
- Never commit `.env` or credential files to source control. `.gitignore` already ignores `.env`.
- Prefer instance/service-account credentials or workload identity (GCP) over long-lived JSON keys.
- Use a secrets manager (e.g., Secret Manager, Vault) in production.
- Limit scope of credentials and rotate them regularly.

Running the quick Reddit test
---------------------------
A small test script exists at `scripts/test_reddit_run.py` which will authenticate to Reddit (using credentials from `.env`) and print recent posts from the first subreddit configured in `src/config/settings.py`.

To run the test locally using the project venv:

```powershell
$env:PYTHONPATH = "${PWD}\src"; C:/Users/Trudy/ingestion_engine/.venv/Scripts/python.exe scripts/test_reddit_run.py
```

This script only prints posts to the console and does not persist them to Google Cloud Storage.

Secrets helpers
---------------
To avoid putting credentials in a `.env` file for local testing, you can store secrets in a secrets backend and load them into your session using the helper scripts:

- PowerShell (Windows, uses SecretManagement/SecretStore):

```powershell
.\scripts\load_secrets_and_run.ps1 -VaultName LocalStore
```

- POSIX (macOS/Linux):

```bash
source ./scripts/load_secrets_and_run.sh --run
```

Both helpers print redacted diagnostics and set the following environment variables in the current session if available: `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USER_AGENT`, `GCS_CREDENTIALS_JSON`, `GCS_BUCKET_NAME`.

If you prefer not to keep a `.env` file in the repo, you may safely delete it; the code will fall back to process environment variables or SecretManagement helpers. Never commit secret files to source control.

Getting started
---------------
1. Create and activate a virtual environment:

```powershell
python -m venv .venv
. .venv/Scripts/Activate.ps1
```

2. Install the package and dev dependencies:

```powershell
python -m pip install --upgrade pip
pip install -e .[dev]
```

3. Run the coordinator from the installed console script (test mode, no persistence):

```powershell
ingestion-coordinator --skip-persist
```

Or run the module directly from a checkout (useful for development):

```bash
python -m src.cli.coordinator --skip-persist
```

Testing
-------
- Run unit tests:

```bash
pytest -q
```

- Integration tests are gated and only run when you explicitly enable them.
	In CI we use a repository secret `RUN_INTEGRATION_TESTS` set to `true` to
	trigger the `integration` job. Locally you can run them by setting up
	credentials (Reddit + GCS) and running:

```bash
pytest -q -m integration
```

Security reminder: ensure credentials provided locally are stored in your OS
secret store or environment and not committed to the repository.

CI Secrets (what to set)
-----------------------
To run full end-to-end integration tests in CI you must add a few repository secrets in GitHub. At minimum set the following in the repository's Settings → Secrets → Actions (or as organization secrets):

- RUN_INTEGRATION_TESTS = true
- REDDIT_CLIENT_ID
- REDDIT_CLIENT_SECRET
- REDDIT_USER_AGENT
- GCS_CREDENTIALS_JSON (the full service account JSON contents)
- GCS_BUCKET_NAME

How to add secrets (GitHub web UI)
---------------------------------
1. Go to your repository on GitHub.
2. Settings → Secrets and variables → Actions → New repository secret.
3. Enter the secret name (one of the names above) and the secret value, then Save.

How to add secrets (gh CLI) — PowerShell examples
------------------------------------------------
Install the GitHub CLI (gh) and authenticate first (`gh auth login`). Then run, for example:

```powershell
# Mark CI to run integration tests
gh secret set RUN_INTEGRATION_TESTS --body true

# Reddit credentials
gh secret set REDDIT_CLIENT_ID --body "<your-reddit-client-id>"
gh secret set REDDIT_CLIENT_SECRET --body "<your-reddit-client-secret>"
gh secret set REDDIT_USER_AGENT --body "IngestionEngine/1.0 (by u/YourUsername)"

# GCS bucket name
gh secret set GCS_BUCKET_NAME --body "your-gcs-bucket-name"

# GCS credentials JSON from a local file (PowerShell):
gh secret set GCS_CREDENTIALS_JSON --body "$(Get-Content C:\path\to\service-account.json -Raw)"
```

How to add secrets (gh CLI) — Bash examples
-------------------------------------------
```bash
# Mark CI to run integration tests
gh secret set RUN_INTEGRATION_TESTS --body true

# Reddit credentials
gh secret set REDDIT_CLIENT_ID --body "<your-reddit-client-id>"
gh secret set REDDIT_CLIENT_SECRET --body "<your-reddit-client-secret>"
gh secret set REDDIT_USER_AGENT --body "IngestionEngine/1.0 (by u/YourUsername)"

# GCS bucket name
gh secret set GCS_BUCKET_NAME --body "your-gcs-bucket-name"

# GCS credentials JSON from a local file (bash):
gh secret set GCS_CREDENTIALS_JSON --body "$(cat /path/to/service-account.json)"
```

Security notes
--------------
- Use repository secrets for repo-scoped CI; use organization-level secrets for multiple repos.
- Do not hard-code secrets in code or commit them to the repository.
- Prefer short-lived credentials or least-privilege service accounts for GCS access.
- Rotate secrets regularly and remove `RUN_INTEGRATION_TESTS` or set it to `false` when you do not want integration jobs to run.

When you're ready and the secrets are added, push your changes and the `integration` job will run automatically when `RUN_INTEGRATION_TESTS` is `true`.

## Contributing

This project is ongoing and forms a key component for a **Media Intelligence Platform** prototype. Feel free to explore, provide feedback, or suggest improvements.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Designed and Developed by Elikplim Kudowor.**
