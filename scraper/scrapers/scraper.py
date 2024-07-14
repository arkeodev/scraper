from abc import ABC, abstractmethod


class Scraper(ABC):
    def __init__(self, source: str):
        """
        Initializes the Scraper instance.

        Args:
            source str: The definition of the source to be scraped
        """
        self.source = source

    @abstractmethod
    def scrape(self):
        """
        Scrape data from the source.

        Returns:
            List[str]: List of documents scraped.
        """
        pass

    def __str__(self):
        return f"{self.__class__.__name__} at {self.source}"

    def __repr__(self):
        return f"{self.__class__.__name__}(url={self.source!r})"
