import asyncio
from src.core.coordinator import IngestionCoordinator


def run(skip_persist: bool = False) -> None:
    """Run the ingestion coordinator.

    This wrapper is intentionally synchronous so it is easy for
    scripts and tests to invoke it without dealing with asyncio
    event loop setup.
    """
    coordinator = IngestionCoordinator(skip_persist=skip_persist)
    asyncio.run(coordinator.run())


def main() -> None:
    """Console entrypoint. Parses simple CLI flags."""
    import argparse

    parser = argparse.ArgumentParser(prog="ingestion-coordinator")
    parser.add_argument("--skip-persist", action="store_true", help="Run in test mode without persisting to GCS")
    args = parser.parse_args()
    run(skip_persist=args.skip_persist)


if __name__ == "__main__":
    main()
