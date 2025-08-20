import asyncio
from typing import List, Any, Optional
from datetime import datetime

from .base_strategy import IngestionStrategy
from ...core.models import Source, Post
from ...config.settings import load_settings

# Optional async/sync PRAW imports
try:
    import asyncpraw as praw_async  # type: ignore
except Exception:
    praw_async = None

try:
    import praw  # type: ignore
except Exception:
    praw = None


class RedditIngestionStrategy(IngestionStrategy):
    """Concrete ingestion strategy for Reddit with clearer error handling."""

    def __init__(self, source: Source):
        # Explicit two-argument super to be robust in all contexts.
        super(RedditIngestionStrategy, self).__init__(source)
        self.settings = load_settings()
        self.reddit: Any = None
        self.using_asyncpraw: bool = False

    async def authenticate(self) -> None:
        """Authenticate using asyncpraw when available, else fallback to praw."""
        client_id = (self.settings.REDDIT_CLIENT_ID or "").strip()
        client_secret = (self.settings.REDDIT_CLIENT_SECRET or "").strip()

        if not client_id or client_id.startswith("your_"):
            print("Reddit credentials missing or look like placeholders; update .env or env vars.")
            self.reddit = None
            return

        try:
            if praw_async is not None:
                # Async PRAW
                self.reddit = praw_async.Reddit(
                    client_id=client_id,
                    client_secret=client_secret,
                    user_agent=self.settings.REDDIT_USER_AGENT or "IngestionEngine/1.0 (by u/Playful_Concert3298)",
                )
                self.using_asyncpraw = True
                await self.reddit.user.me()
                print(f"Authenticated with Async PRAW for source: {self.source.name}")
                return

            if praw is not None:
                # Sync PRAW fallback; run blocking calls in thread.
                self.reddit = praw.Reddit(
                    client_id=client_id,
                    client_secret=client_secret,
                    user_agent=self.settings.REDDIT_USER_AGENT or "IngestionEngine/1.0 (by u/Playful_Concert3298)",
                )
                await asyncio.to_thread(lambda: self.reddit.user.me())  # type: ignore[attr-defined]
                print(f"Authenticated with PRAW for source: {self.source.name}")
                return

            print("Neither asyncpraw nor praw is installed; cannot authenticate to Reddit.")
            self.reddit = None
        except Exception as exc:
            print(f"Reddit authentication failed for {self.source.name}: {type(exc).__name__}: {exc}")
            self.reddit = None

    async def ingest_data(self) -> List[Post]:
        if not self.reddit:
            print("Authentication not completed. Skipping ingestion.")
            return []
        # Normalize subreddit names so callers can pass 'r/Name', '/r/Name', full URLs,
        # or just the bare subreddit. This prevents passing invalid values to PRAW
        # which can result in 400 BadRequest responses.
        def _normalize_subreddit_name(name: str) -> str:
            if not name:
                return ""
            n = name.strip()
            # If a full URL was provided, attempt to extract the subreddit segment.
            if "reddit.com" in n:
                # Look for the '/r/<sub>' pattern
                idx = n.find("/r/")
                if idx != -1:
                    n = n[idx + 3 :]
            # Remove leading '/r/' or 'r/' prefixes
            if n.startswith("/r/"):
                n = n[3:]
            elif n.startswith("r/"):
                n = n[2:]
            # Strip any leading/trailing slashes and take the last path segment
            n = n.strip("/ ")
            if "/" in n:
                parts = [p for p in n.split("/") if p]
                if parts:
                    n = parts[-1]
            return n

        subreddit_name = _normalize_subreddit_name(self.source.name)
        posts: List[Post] = []

        try:
            if self.using_asyncpraw:
                # asyncpraw: subreddit() is a coroutine in some versions and must be awaited.
                print(f"Using subreddit: {subreddit_name} (normalized from {self.source.name})")
                subreddit = await self.reddit.subreddit(subreddit_name)  # type: ignore
                # asyncpraw's listing yields an async generator
                async for submission in subreddit.hot(limit=25):  # type: ignore
                    posts.append(self._normalize_submission(submission))
            else:
                def _sync_fetch():
                    sub = self.reddit.subreddit(subreddit_name)  # type: ignore[attr-defined]
                    return list(sub.hot(limit=25))  # type: ignore[attr-defined]

                submissions = await asyncio.to_thread(_sync_fetch)
                for submission in submissions:
                    posts.append(self._normalize_submission(submission))

            print(f"Ingested {len(posts)} posts from subreddit: {subreddit_name}")
            return posts
        except Exception as exc:
            print(f"Error ingesting from {subreddit_name}: {type(exc).__name__}: {exc}")
            return []
        finally:
            # Close asyncpraw client session if we created one to avoid resource warnings.
            try:
                if self.using_asyncpraw and getattr(self.reddit, "close", None):
                    await self.reddit.close()  # type: ignore
            except Exception:
                # Best-effort cleanup; do not mask the main exception path.
                pass

    def _normalize_submission(self, submission: object) -> Post:
        # Defensive attribute access for third-party objects
        author = getattr(submission, "author", None)
        author_name = getattr(author, "name", "Deleted") if author else "Deleted"
        created = getattr(submission, "created_utc", None)
        if created:
            created_at = datetime.fromtimestamp(created)
        else:
            created_at = datetime.utcnow()

        return Post(
            source_id=self.source.id,
            title=getattr(submission, "title", ""),
            content=getattr(submission, "selftext", ""),
            author=author_name,
            url=getattr(submission, "url", ""),
            created_at=created_at,
            metadata={
                "score": getattr(submission, "score", 0),
                "num_comments": getattr(submission, "num_comments", 0),
            },
        )
