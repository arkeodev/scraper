from dataclasses import dataclass


@dataclass
class MilvusConfig:
    host: str = "localhost"
    port: str = "19530"
    collection_name: str = "document_collection"  # Dynamic per URL
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"


@dataclass
class AppConfig:
    requests_per_minute: int = 10
    min_interval_between_requests: float = (
        60 / 10
    )  # Calculated from requests per minute
