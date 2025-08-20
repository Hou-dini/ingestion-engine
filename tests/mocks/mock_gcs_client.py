from typing import List
from src.core.models import Post


class MockGCSClient:
    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        self.saved = {}  # filename -> json string or posts list
        self.authenticated = False

    def authenticate(self):
        # Simulate successful authentication
        self.authenticated = True

    def save_posts_as_json(self, posts: List[Post], filename: str) -> None:
        # Store the posts in memory as dicts for assertions
        self.saved[filename] = [p.__dict__ for p in posts]
        print(f"[mock_gcs] saved {len(posts)} posts to {filename}")

    def load_posts_from_json(self, filename: str) -> List[Post]:
        data = self.saved.get(filename, [])
        return [Post(**item) for item in data]
