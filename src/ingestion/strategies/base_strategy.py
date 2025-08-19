from abc import ABC, abstractmethod
from typing import List

# We import the models we've already defined.
from ...core.models import Source, Post


class IngestionStrategy(ABC):
    """
    An abstract base class for all data ingestion strategies.

    This class defines the required interface for any ingestion method,
    ensuring that each one can be used interchangeably by the main
    ingestion engine. This is a crucial step for our "normalization" layer.
    """

    def __init__(self, source: Source):
        """
        Initializes the strategy with a specific data source.

        Args:
            source: The Source object containing details about the data source.
        """
        self.source = source

    @abstractmethod
    async def ingest_data(self) -> List[Post]:
        """
        The main method to execute the data ingestion process.

        This method must be implemented by all concrete subclasses.
        It should handle the logic for connecting to the source,
        retrieving the raw data, and normalizing it into a list of Post objects.

        Returns:
            A list of Post objects representing the normalized data.
        """
        raise NotImplementedError()

    @abstractmethod
    async def authenticate(self) -> None:
        """
        Authenticates with the data source if required.

        This method should be implemented to handle any necessary
        authentication steps (e.g., API keys, OAuth tokens).
        """
        raise NotImplementedError()
