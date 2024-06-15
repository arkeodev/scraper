"""
Configuration module for application settings.
"""

from dataclasses import dataclass


@dataclass
class AppConfig:
    requests_per_minute: int = 10
    min_interval_between_requests: float = (
        60 / 10
    )  # Calculated from requests per minute


@dataclass
class ScraperConfig:
    max_links: int = 10
    page_load_timeout: int = 10
    page_load_sleep: int = 5
    scraping_depth: int = 1
    min_document_length_to_read: int = 100


@dataclass
class QAConfig:
    top_n_chunks: int = 5
