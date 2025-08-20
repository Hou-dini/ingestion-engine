import json
import pytest
from src.config.settings import load_settings
from src.cli.coordinator import run


@pytest.mark.integration
def test_integration_coordinator_end_to_end():
    """End-to-end smoke test that runs the coordinator and persists to GCS.

    This test is skipped unless GCS and Reddit credentials are provided in
    the environment (or via your secret store). It is intended for local
    integration testing only and should be excluded from CI by default.
    """
    settings = load_settings()

    # Require both Reddit and GCS credentials for the full integration test
    if not settings.REDDIT_CLIENT_ID or settings.REDDIT_CLIENT_ID.startswith("your_"):
        pytest.skip("Reddit credentials not configured; skipping integration test")
    if not settings.GCS_CREDENTIALS_JSON or not settings.GCS_BUCKET_NAME:
        pytest.skip("GCS credentials not configured; skipping integration test")

    # Run coordinator normally (do not skip persist). This will perform network IO.
    run(skip_persist=False)

    # If we get here without exception, consider it a success. More assertions
    # (e.g., verifying objects exist in the bucket) can be added if desired.
    assert True
