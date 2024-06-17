"""
Configuration module for application settings.
"""

from dataclasses import dataclass


@dataclass
class AppConfig:
    """
    Configuration for application-wide settings.

    Attributes:
        requests_per_minute (int): The maximum number of requests per minute.
        min_interval_between_requests (float): The minimum interval between requests in seconds, calculated from requests per minute.
    """

    requests_per_minute: int = 10
    min_interval_between_requests: float = (
        60 / 10
    )  # Calculated from requests per minute to determine the minimum interval between requests.


@dataclass
class ScraperConfig:
    """
    Configuration for the web scraper settings.

    Attributes:
        max_links (int): The maximum number of links to scrape.
        page_load_timeout (int): The timeout for loading a page, in seconds.
        page_load_sleep (int): The sleep time after loading a page, in seconds.
        scraping_depth (int): The maximum depth for recursive scraping.
        min_document_length_to_read (int): The minimum length of a document to be considered for reading.
    """

    max_links: int = 10
    page_load_timeout: int = 10
    page_load_sleep: int = 5
    scraping_depth: int = 1
    min_document_length_to_read: int = 100  # Minimum length for a document to be read.


@dataclass
class QAConfig:
    """
    Configuration for the question-answering settings.

    Attributes:
        top_n_chunks (int): The number of top chunks to consider for question answering.
    """

    top_n_chunks: int = 5
