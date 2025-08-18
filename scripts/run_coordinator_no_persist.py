import asyncio
from core.coordinator import IngestionCoordinator
from storage.gcs_client import GCSClient


if __name__ == '__main__':
    # Monkeypatch GCSClient.save_posts_as_json to avoid external persistence during test
    original_save = GCSClient.save_posts_as_json

    def noop_save(self, posts, filename):
        print(f"[TEST MODE] Would save {len(posts)} posts to {filename}")

    GCSClient.save_posts_as_json = noop_save

    try:
        coordinator = IngestionCoordinator()
        asyncio.run(coordinator.run())
    finally:
        # Restore original method
        GCSClient.save_posts_as_json = original_save
