"""
Configuration module for application settings.
"""

from dataclasses import dataclass


@dataclass
class ScraperConfig:
    """
    Configuration for the web scraper settings.

    Attributes:
        page_load_timeout (int): The timeout for loading a page, in seconds.
        page_load_sleep (int): The sleep time after loading a page, in seconds.
    """

    page_load_timeout: int = 10
    page_load_sleep: int = 5


# Matches the embedding model names with the language
embedding_models_dict = {
    "turkish": "emrecan/bert-base-turkish-cased-mean-nli-stsb-tr",
    "english": "BAAI/bge-small-en-v1.5",
}
