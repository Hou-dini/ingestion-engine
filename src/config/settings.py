import os
from dataclasses import dataclass, field
from typing import List, Dict
from dotenv import load_dotenv, find_dotenv

# Load environment variables from a .env file located in the repository root.
# Using find_dotenv() makes the loader robust to different working directories
# (for example when modules are imported from scripts or tests).
dotenv_path = find_dotenv()
if dotenv_path:
    # Force overriding any existing environment variables in the process
    # so that values in the project's .env take precedence during local runs.
    load_dotenv(dotenv_path, override=True)


@dataclass
class IngestionSources:
    """
    A dataclass to hold the sources we defined in the curated_sources_for_mvp.txt file.
    This provides a clean, structured way to access our source URLs and other details.
    """
    subreddits: List[str] = field(default_factory=list)
    youtube_channels: Dict[str, str] = field(default_factory=dict)
    industry_blogs: List[str] = field(default_factory=list)


@dataclass
class Settings:
    """
    This dataclass holds all the configuration settings for our application.
    Using a dataclass provides a simple, readable way to store configuration.
    """
    # --- API Keys and Secrets ---
    # We use os.getenv() to retrieve environment variables. This keeps sensitive data
    # out of our codebase and makes our application more secure.
    # Leave fields blank here; populate them in `load_settings()` so
    # environment variables are read at runtime and reflect any changes
    # made before `load_settings()` is called.
    REDDIT_CLIENT_ID: str = ""
    REDDIT_CLIENT_SECRET: str = ""
    REDDIT_USER_AGENT: str = ""

    # --- Google Cloud Storage (GCS) Configuration ---
    GCS_BUCKET_NAME: str = os.getenv("GCS_BUCKET_NAME", "your-gcs-bucket-name")
    GCS_CREDENTIALS_JSON: str = os.getenv("GCS_CREDENTIALS_JSON", "")

    # --- Ingestion Configuration ---
    # This stores the URLs and information for the sources we will be ingesting.
    # We will populate these fields later in our `load_settings` function.
    sources: IngestionSources = field(default_factory=IngestionSources)


def load_settings() -> Settings:
    """
    This function creates and returns an instance of our Settings object.
    We can add more complex logic here later, like loading sources from a file
    or performing validation checks.
    """
    settings = Settings()

    # Read environment variables at runtime. We provide the same defaults
    # used previously so behavior is unchanged if no .env or env vars exist.
    settings.REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "SRo-AZLgsKclg-ZgjOhrlg")
    settings.REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "fJQiNSFrLJDJh5q1k7yg7_kc0RPr8g")
    settings.REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "ForesightEngine/1.0 (by u/Playful_Concert3298)")

    settings.GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "your-gcs-bucket-name")
    settings.GCS_CREDENTIALS_JSON = os.getenv("GCS_CREDENTIALS_JSON", "")

    # In a real-world scenario, we would parse the curated_sources_for_mvp.txt file
    # to dynamically populate the `sources` field. For now, we'll hardcode some
    # placeholders to show the structure.
    settings.sources.subreddits = ["r/BuyItForLife", "r/SkincareAddiction"]
    settings.sources.youtube_channels = {
        "MKBHD": "https://www.youtube.com/channel/UC-N1_h8Jg_Fj75R47E2lXJw",
        "Vogue": "https://www.youtube.com/channel/UCVv7qg-m4T3K-i0I6YhKjJg"
    }
    settings.sources.industry_blogs = [
        "https://www.adweek.com/feed",
        "https://www.adage.com/rss.xml"
    ]

    return settings
