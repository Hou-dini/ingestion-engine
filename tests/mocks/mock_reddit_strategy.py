from typing import List
from src.core.models import Post, Source
from src.ingestion.strategies.base_strategy import IngestionStrategy


class MockRedditStrategy(IngestionStrategy):
    def __init__(self, source: Source):
        super().__init__(source)
        self.authenticated = False

    async def authenticate(self) -> None:
        self.authenticated = True

    async def ingest_data(self) -> List[Post]:
        # Return a single fake post
        return [
            Post(
                source_id=self.source.id,
                title="Mock post",
                content="This is a mocked reddit post",
                author="mock_user",
                url="https://reddit.mock/post/1",
            )
        ]
