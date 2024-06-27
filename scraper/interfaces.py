from abc import ABC, abstractmethod
from typing import List


class Scraper(ABC):
    """
    Abstract class for scraping and index creation.
    """

    @abstractmethod
    def scrape(self):
        """Scrape data from the source."""
        pass

    def __str__(self):
        return "Scraper"

    def __repr__(self):
        return f"Scraper()"


class Rag(ABC):
    """RAG abstract class."""

    def __init__(self, documents: List[str], model_config: dict):
        """
        Initializes the RAG instance with a list of documents.

        Args:
            documents (List[str]): A list of documents as strings.
            model_config: Model configuration.
        """
        self.documents = documents
        self.model_config = model_config

    @abstractmethod
    def rag(self, prompt: str) -> str:
        """Return the most similar retrieval results for the given question.

        Args:
            prompt str: The user prompt.

        Returns:
            str: A string of matching documents.
        """
        pass

    @abstractmethod
    def query(self, context: str) -> str:
        """Return the llm result for the given context.

        Args:
            index (Index): The index to search.

        Returns:
            List[str]: A list of matching documents.
        """
        pass

    def __str__(self):
        return "RAGAbstract"

    def __repr__(self):
        return f"RAGAbstract()"


class Query(ABC):
    """Query abstract class."""

    def __str__(self):
        return "QueryAbstract"

    def __repr__(self):
        return f"QueryAbstract()"
