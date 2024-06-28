"""
Configuration module for application settings.
"""

from typing import Optional

from pydantic import BaseModel, Field

# Matches the embedding model names with the language
embedding_models_dict = {
    "turkish": "emrecan/bert-base-turkish-cased-mean-nli-stsb-tr",
    "english": "BAAI/bge-small-en-v1.5",
}


class ScraperConfig(BaseModel):
    """
    Configuration for the web scraper settings.

    Attributes:
        page_load_timeout (int): The timeout for loading a page, in seconds.
        page_load_sleep (int): The sleep time after loading a page, in seconds.
    """

    page_load_timeout: int = 10
    page_load_sleep: int = 5


class LLMConfig(BaseModel):
    llm_model_name: str
    api_key: str = None
    embedding_model_name: str
    temperature: Optional[float] = Field(0.7, ge=0.0, le=1.0)
    max_tokens: Optional[int] = Field(10_000, gt=0)


class RAGConfig(BaseModel):
    task_definition: str = None
    llm_config: LLMConfig
    vector_store_path: str = None
    query: str = None
