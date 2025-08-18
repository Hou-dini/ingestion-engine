import asyncio
from typing import List, Optional
from datetime import datetime

from ingestion.strategies.base_strategy import IngestionStrategy
from core.models import Source, Post
from config.settings import load_settings

# Prefer asyncpraw when available to avoid running sync PRAW in async contexts.
try:
    import asyncpraw as praw_async  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    praw_async = None

try:
    import praw  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    praw = None


class RedditIngestionStrategy(IngestionStrategy):
    """
    A concrete implementation of the IngestionStrategy for Reddit.
    
    This class handles authentication, data retrieval from Reddit, and
    normalization of the data into our core Post model.
    """

    def __init__(self, source: Source):
        """
        Initializes the Reddit strategy with a specific source.
        We also load the application settings here to get our API keys.
        """
    super().__init__(source)
    self.settings = load_settings()
    self.reddit = None
    self._using_asyncpraw = False

    async def authenticate(self) -> None:
        """
        Authenticates with the Reddit API using PRAW.
        
        This method uses the client ID and secret from our settings to create
        a Reddit instance. The `readonly` flag ensures we don't accidentally
        perform any write operations.
        """
        try:
            if praw_async is not None:
                # Use asyncpraw which is designed for asyncio.
                self.reddit = praw_async.Reddit(
                    client_id=self.settings.REDDIT_CLIENT_ID,
                    client_secret=self.settings.REDDIT_CLIENT_SECRET,
                    user_agent=self.settings.REDDIT_USER_AGENT or "ForesightEngine/1.0"
                )
                self._using_asyncpraw = True
                # Validate credentials by making a lightweight async request.
                await self.reddit.user.me()
                print(f"Successfully authenticated with Async PRAW for source: {self.source.name}")
            elif praw is not None:
                # Fall back to synchronous PRAW but run blocking calls in a thread.
                self.reddit = praw.Reddit(
                    client_id=self.settings.REDDIT_CLIENT_ID,
                    client_secret=self.settings.REDDIT_CLIENT_SECRET,
                    user_agent=self.settings.REDDIT_USER_AGENT or "ForesightEngine/1.0"
                )
                await asyncio.to_thread(lambda: self.reddit.user.me())  # type: ignore[attr-defined]
                print(f"Successfully authenticated with PRAW for source: {self.source.name}")
            else:
                raise RuntimeError("No PRAW or Async PRAW installation found")
        except Exception as e:
            print(f"Authentication failed for Reddit source: {self.source.name} with error: {e}")
            self.reddit = None

    async def ingest_data(self) -> List[Post]:
        """
        Ingests data from the specified Reddit subreddit.
        
        This method retrieves the 'hot' posts from the subreddit, transforms
        each post into a Post object, and returns a list of them.
        """
        if not self.reddit:
            print("Authentication failed. Cannot ingest data.")
            return []

        subreddit_name = self.source.name

        try:
            posts: List[Post] = []

            if self._using_asyncpraw:
                # asyncpraw returns an async generator for listings
                # reddit.subreddit(...) returns a Subreddit object (not awaitable).
                subreddit = self.reddit.subreddit(subreddit_name)
                async for submission in subreddit.hot(limit=25):
                    post = Post(
                        source_id=self.source.id,
                        title=submission.title,
                        content=getattr(submission, "selftext", ""),
                        author=getattr(submission.author, "name", "Deleted") if submission.author else "Deleted",
                        url=submission.url,
                        created_at=datetime.fromtimestamp(submission.created_utc),
                        metadata={
                            "score": getattr(submission, "score", 0),
                            "num_comments": getattr(submission, "num_comments", 0)
                        }
                    )
                    posts.append(post)
            else:
                # Synchronous PRAW: run blocking calls in a thread
                def _sync_fetch():
                    subreddit = self.reddit.subreddit(subreddit_name)  # type: ignore[attr-defined]
                    return list(subreddit.hot(limit=25))  # type: ignore[attr-defined]

                submissions = await asyncio.to_thread(_sync_fetch)
                for submission in submissions:
                    post = Post(
                        source_id=self.source.id,
                        title=submission.title,
                        content=getattr(submission, "selftext", ""),
                        author=submission.author.name if submission.author else "Deleted",
                        url=submission.url,
                        created_at=datetime.fromtimestamp(submission.created_utc),
                        metadata={
                            "score": getattr(submission, "score", 0),
                            "num_comments": getattr(submission, "num_comments", 0)
                        }
                    )
                    posts.append(post)

            print(f"Ingested {len(posts)} posts from subreddit: {subreddit_name}")
            return posts

        except Exception as e:
            print(f"An error occurred during Reddit ingestion for source: {self.source.name}: {e}")
            return []
