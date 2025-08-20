import pytest
from src.config.settings import load_settings
from src.ingestion.strategies.reddit_strategy import RedditIngestionStrategy
from src.core.models import Source


@pytest.mark.asyncio
async def test_reddit_run_integration():
    """Light integration test that runs the Reddit ingestion strategy once.

    This test is skipped when Reddit credentials are not configured. It is
    intended for local/integration runs and will be ignored in CI unless
    you populate credentials in the environment or secret store.
    """
    settings = load_settings()

    # Skip if credentials are missing or look like placeholders
    if not settings.REDDIT_CLIENT_ID or settings.REDDIT_CLIENT_ID.startswith("your_"):
        pytest.skip("Reddit credentials not configured; skipping integration test")

    subreddits = settings.sources.subreddits
    if not subreddits:
        pytest.skip("No subreddits configured in settings; skipping")

    subreddit = subreddits[0]
    source = Source(name=subreddit, url=f"https://reddit.com/{subreddit}", type="reddit")

    strategy = RedditIngestionStrategy(source)
    await strategy.authenticate()
    posts = await strategy.ingest_data()

    assert isinstance(posts, list)
    # Basic sanity checks
    if posts:
        assert hasattr(posts[0], "title")
        assert hasattr(posts[0], "content")
