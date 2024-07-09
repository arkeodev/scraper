"""
Configuration module for application settings.
"""

from collections import namedtuple
from typing import Optional

from pydantic import BaseModel, Field

Task = namedtuple("Task", ["id", "task_definition", "allowed_extensions", "is_url"])

# Define the task instances
tasks = [
    Task(id=1, task_definition="Parse a URL", allowed_extensions=["url"], is_url=True),
    Task(
        id=2,
        task_definition="Parse PDF file(s)",
        allowed_extensions=["pdf"],
        is_url=False,
    ),
    Task(
        id=3,
        task_definition="Parse E-pub file(s)",
        allowed_extensions=["epub"],
        is_url=False,
    ),
]

# Matches the embedding model names with the language
embedding_models_dict = {
    "turkish": "emrecan/bert-base-turkish-cased-mean-nli-stsb-tr",
    "english": "text-embedding-ada-002",
}


class LLMConfig(BaseModel):
    model_name: str
    api_key: str = None
    embedding_model_name: str
    temperature: Optional[float] = Field(0.7, ge=0.0, le=1.0)
    max_tokens: Optional[int] = Field(1_000, gt=0)
