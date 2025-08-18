import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.core.coordinator import IngestionCoordinator
from src.core.models import Post, Source


@pytest.mark.asyncio
async def test_run_with_mocked_services(monkeypatch):
    # Create coordinator
    coordinator = IngestionCoordinator()

    # Mock GCSClient methods
    mock_gcs = MagicMock()
    mock_gcs.authenticate = MagicMock()
    mock_gcs.save_posts_as_json = MagicMock()

    monkeypatch.setattr(coordinator, 'gcs_client', mock_gcs)

    # Mock Reddit strategy to avoid real API calls
    class DummyStrategy:
        def __init__(self, source: Source):
            self.source = source

        async def authenticate(self):
            return None

        async def ingest_data(self):
            return [Post(source_id=self.source.id, title='t', content='c')]

    coordinator.strategies = {'reddit': DummyStrategy}

    # Run coordinator.run but with a single subreddit in settings
    coordinator.settings.sources.subreddits = ['r/test']

    await coordinator._setup_services()
    # Run ingestion for one source
    await coordinator.run()

    # Expect that save_posts_as_json was called
    assert mock_gcs.save_posts_as_json.called
