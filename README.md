# Foresight Engine

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
$env:PYTHONPATH = "${PWD}\src"; C:/Users/Trudy/foresight_engine/.venv/Scripts/python.exe scripts/test_reddit_run.py
```

This script only prints posts to the console and does not persist them to Google Cloud Storage.
