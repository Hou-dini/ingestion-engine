import asyncio
from src.core.coordinator import IngestionCoordinator
from tests.mocks.mock_gcs_client import MockGCSClient
from tests.mocks.mock_reddit_strategy import MockRedditStrategy


def test_coordinator_with_mocks(monkeypatch):
    # Create coordinator with skip_persist False so it attempts to save
    coordinator = IngestionCoordinator(skip_persist=False)

    # Replace GCS client instance with mock
    mock_gcs = MockGCSClient(bucket_name="test_bucket")
    mock_gcs.authenticate()
    monkeypatch.setattr(coordinator, "gcs_client", mock_gcs)

    # Replace reddit strategy with mock
    monkeypatch.setitem(coordinator.strategies, "reddit", MockRedditStrategy)

    # Run the coordinator
    asyncio.run(coordinator.run())

    # After run, ensure something was saved to the mock GCS
    assert any(mock_gcs.saved), "No files saved to mock GCS"
