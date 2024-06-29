from abc import ABC, abstractmethod
from typing import List


class Scraper(ABC):
    def __init__(self, url: str):
        """
        Initializes the Scraper instance.

        Args:
            url str: The url to be scraped
        """
        self.url = url

    @abstractmethod
    def scrape(self):
        """
        Scrape data from the source.

        Returns:
            List[str]: List of documents scraped.
        """
        pass

    def __str__(self):
        return f"{self.__class__.__name__} at {self.url}"

    def __repr__(self):
        return f"{self.__class__.__name__}(url={self.url!r})"


class Rag(ABC):
    def __init__(self, documents: List[str], model_config: dict):
        """
        Initializes the RAG instance.

        Args:
            documents (List[str]): A list of documents as strings.
            model_config: Model configuration.
        """
        self.documents = documents
        self.model_config = model_config

    @abstractmethod
    def execute(self, prompt: str) -> str:
        """
        Gets the user prompt and generate an LLM response vie retrieval documents.

        Args:
            prompt str: The user prompt.

        Returns:
            str: LLM response.
        """
        pass

    def __str__(self):
        return "RAGAbstract"

    def __repr__(self):
        return f"RAGAbstract()"
