import asyncio
from config.settings import load_settings
from ingestion.strategies.reddit_strategy import RedditIngestionStrategy
from core.models import Source


async def main():
    settings = load_settings()
    subreddits = settings.sources.subreddits
    if not subreddits:
        print("No subreddits configured in settings.")
        return

    subreddit = subreddits[0]
    source = Source(name=subreddit, url=f'https://reddit.com/{subreddit}', type='reddit')

    strategy = RedditIngestionStrategy(source)
    await strategy.authenticate()
    posts = await strategy.ingest_data()

    print(f"Retrieved {len(posts)} posts from {subreddit}:")
    for p in posts:
        print('-', p.title, '|', p.author, '|', p.url)


if __name__ == '__main__':
    asyncio.run(main())
