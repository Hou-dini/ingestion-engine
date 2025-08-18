import asyncio
from datetime import datetime
from unittest.mock import MagicMock

import pytest

from src.ingestion.strategies.reddit_strategy import RedditIngestionStrategy
from src.core.models import Source, Post


class DummySubmission:
    def __init__(self, title, selftext, author_name, url, created_utc, score, num_comments):
        self.title = title
        self.selftext = selftext
        self.author = MagicMock(name='author')
        self.author.name = author_name
        self.url = url
        self.created_utc = created_utc
        self.score = score
        self.num_comments = num_comments


@pytest.mark.asyncio
async def test_reddit_ingest(monkeypatch):
    # Create dummy reddit object
    dummy_reddit = MagicMock()

    submissions = [DummySubmission('t1', 'c1', 'a1', 'url1', 1600000000, 10, 2), DummySubmission('t2', 'c2', None, 'url2', 1600000100, 5, 1)]

    class DummySubreddit:
        def hot(self, limit=None):
            return submissions

    dummy_reddit.subreddit.return_value = DummySubreddit()
    dummy_reddit.user.me.return_value = None

    src = Source(name='r/test', url='https://reddit.com/r/test', type='reddit')

    strategy = RedditIngestionStrategy(src)
    strategy.reddit = dummy_reddit

    await strategy.authenticate()
    posts = await strategy.ingest_data()

    assert isinstance(posts, list)
    assert all(isinstance(p, Post) for p in posts)
    assert posts[0].title == 't1'
    assert posts[1].author == 'Deleted' or posts[1].author is not None
