import asyncio
from typing import Dict, Type, List

from ..config.settings import load_settings, Settings
from .models import Source, Post
from ..ingestion.strategies.base_strategy import IngestionStrategy
from ..ingestion.strategies.reddit_strategy import RedditIngestionStrategy
from ..storage.gcs_client import GCSClient

class IngestionCoordinator:
    """
    The central coordinator for the data ingestion pipeline.
    
    This class orchestrates the entire workflow:
    1. Loads application settings.
    2. Initializes and authenticates with external services.
    3. Manages and executes different ingestion strategies.
    4. Persists the ingested data to cloud storage.
    """

    def __init__(self, skip_persist: bool = False):
        """Initializes the coordinator and loads settings."""
        self.settings: Settings = load_settings()
        self.skip_persist: bool = skip_persist
        # We map source types to their corresponding strategy classes.
        # This makes the coordinator easily extensible.
        self.strategies: Dict[str, Type[IngestionStrategy]] = {
            "reddit": RedditIngestionStrategy
        }

        # Initialize GCS client instance for persistence.
        self.gcs_client: GCSClient = GCSClient(self.settings.GCS_BUCKET_NAME)

    async def _setup_services(self):
        """Initializes and authenticates all required services."""
        # Authenticate with Google Cloud Storage first.
        await asyncio.to_thread(self.gcs_client.authenticate)
        
        # We can add more service authentications here as we build them,
        # for example, a YouTube API authentication.

    async def ingest_source(self, source_type: str, source_name: str, source_url: str) -> None:
        """
        Ingests data from a single source using the appropriate strategy.
        
        Args:
            source_type: The type of source (e.g., 'reddit').
            source_name: The name of the source (e.g., 'r/BuyItForLife').
            source_url: The URL of the source.
        """
        if source_type not in self.strategies:
            print(f"No ingestion strategy found for type: {source_type}. Skipping.")
            return

        print(f"Starting ingestion for source: {source_name} ({source_type})")
        
        # Create a Source object using the data provided.
        source = Source(name=source_name, url=source_url, type=source_type)
        
        # Instantiate the correct ingestion strategy class.
        strategy_class = self.strategies[source_type]
        strategy = strategy_class(source)

        # Authenticate and ingest data using the strategy.
        await strategy.authenticate()

        posts: List[Post] = await strategy.ingest_data()

        if posts:
            # If we successfully ingested data, save it to GCS.
            filename = f"{source_type}_{source_name.replace('/', '_')}_{source.id}.json"
            await asyncio.to_thread(self.gcs_client.save_posts_as_json, posts, filename)
        else:
            print(f"No data to save for source: {source_name}")

    async def run(self):
        """
        The main entry point for the coordinator.
        
        This method executes the entire pipeline: setup, data ingestion for all
        defined sources, and finalization.
        """
        print("Starting the Ingestion Coordinator...")
        
        # First, set up all our services.
        await self._setup_services()
        
        # We'll use a task list to run all our ingestions concurrently.
        # This is more efficient than running them sequentially.
        ingestion_tasks = []

        # Ingest data from all sources defined in our settings.
        # We'll need a way to pass the full list of sources here from a config file.
        # For now, we'll iterate through our hardcoded example lists from the `settings.py`.
        for subreddit in self.settings.sources.subreddits:
            ingestion_tasks.append(
                self.ingest_source(source_type="reddit", source_name=subreddit, source_url=f"https://www.reddit.com/{subreddit}/")
            )
        
        # We'll need to add logic for YouTube and other sources here once those strategies are built.
        
        if not ingestion_tasks:
            print("No ingestion tasks found. Exiting.")
            return
        
        # Run all the ingestion tasks concurrently and wait for them to finish.
        await asyncio.gather(*ingestion_tasks)
        
        print("Ingestion process complete.")

# A common pattern in Python for making a script runnable directly.
if __name__ == "__main__":
    coordinator = IngestionCoordinator()
    asyncio.run(coordinator.run())
