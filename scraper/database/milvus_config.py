from dataclasses import dataclass


@dataclass
class MilvusConfig:
    host: str = "localhost"
    port: str = "19530"
    collection_name: str = "document_collection"
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
