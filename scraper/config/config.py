"""
Purpose: Contains configuration data classes for Milvus, application settings, scraper settings, and QA settings.
"""

from dataclasses import dataclass


@dataclass
class MilvusConfig:
    host: str = "localhost"
    port: str = "19530"
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"


@dataclass
class AppConfig:
    requests_per_minute: int = 10
    min_interval_between_requests: float = (
        60 / 10
    )  # Calculated from requests per minute


@dataclass
class ScraperConfig:
    max_links: int = 2
    page_load_timeout: int = 15
    page_load_sleep: int = 5


@dataclass
class QAConfig:
    top_n_chunks: int = 5
