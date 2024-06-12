# config.py

from dataclasses import dataclass


@dataclass
class MilvusConfig:
    host: str = "localhost"
    port: str = "19530"
    embedding_model_name: str = "meta-llama/Llama-3-70B"  # Updated to Llama 3


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


@dataclass
class QAConfig:
    top_n_chunks: int = 5
    embedding_model_name: str = "meta-llama/Llama-3-70B"  # Updated to Llama 3
