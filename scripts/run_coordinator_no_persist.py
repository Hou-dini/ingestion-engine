import asyncio
import os
from dotenv import find_dotenv
from core.coordinator import IngestionCoordinator
from storage.gcs_client import GCSClient
from config.settings import load_settings


def redact(v: str) -> str:
    if not v:
        return ""
    if len(v) <= 8:
        return "REDACTED"
    return v[:4] + "..." + v[-4:]


if __name__ == '__main__':
    # Monkeypatch GCSClient.save_posts_as_json to avoid external persistence during test
    original_save = GCSClient.save_posts_as_json

    def noop_save(self, posts, filename):
        print(f"[TEST MODE] Would save {len(posts)} posts to {filename}")

    GCSClient.save_posts_as_json = noop_save

    # Diagnostics: report which .env was found and the redacted settings
    dotenv_path = find_dotenv()
    print(f"Using .env: {dotenv_path}")
    settings = load_settings()
    print("Loaded settings (redacted):")
    print(f"  REDDIT_CLIENT_ID={redact(settings.REDDIT_CLIENT_ID)}")
    print(f"  REDDIT_CLIENT_SECRET={redact(settings.REDDIT_CLIENT_SECRET)}")
    print(f"  REDDIT_USER_AGENT={settings.REDDIT_USER_AGENT}")

    try:
        coordinator = IngestionCoordinator()
        asyncio.run(coordinator.run())
    finally:
        # Restore original method
        GCSClient.save_posts_as_json = original_save
