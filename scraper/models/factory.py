from collections import namedtuple
from typing import Dict, Type

from langchain.embeddings.base import Embeddings
from langchain_huggingface import HuggingFaceEndpoint
from langchain_huggingface.embeddings.huggingface import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings
from scrapegraphai.models import Anthropic, Groq, OpenAI
from sentence_transformers import SentenceTransformer

from scraper.config import LLMConfig, embedding_models_dict

ModelConfig = namedtuple("ModelConfig", ["llm", "embedder"])


class BaseModelFactory:
    def create_llm(self, config: dict):
        raise NotImplementedError

    def create_embedder(self, config: dict):
        raise NotImplementedError


class OpenAIModelFactory(BaseModelFactory):
    def create_llm(self, config: dict):
        return OpenAI(
            llm_config={
                "model_name": config.get("model_name"),
                "openai_api_key": config.get("api_key"),
                "max_tokens": config.get("max_tokens"),
                "temperature": config.get("temperature"),
            }
        )

    def create_embedder(self, config: dict):
        return OpenAIEmbeddings(
            model=config["embedding_model_name"], api_key=config["api_key"]
        )


class GroqModelFactory(BaseModelFactory):
    def create_llm(self, config: dict):
        return Groq(
            llm_config={
                "model": config.get("model_name"),
                "api_key": config.get("api_key"),
                "max_tokens": config.get("max_tokens"),
                "temperature": config.get("temperature"),
            }
        )

    def create_embedder(self, config: dict):
        return SentenceTransformerEmbeddings()


class AnthropicModelFactory(BaseModelFactory):
    def create_llm(self, config: dict):
        return Anthropic(
            llm_config={
                "model": config.get("model_name"),
                "anthropic_api_key": config.get("api_key"),
                "max_tokens": config.get("max_tokens"),
                "temperature": config.get("temperature"),
            }
        )

    def create_embedder(self, config: dict):
        return SentenceTransformerEmbeddings()


class HuggingFaceModelFactory(BaseModelFactory):
    def create_llm(self, config: dict):
        return HuggingFaceEndpoint(
            repo_id=config.get("model_name"),
            max_new_tokens=config.get("max_tokens"),
            temperature=config.get("temperature"),
            huggingfacehub_api_token=config.get("api_key"),
        )

    def create_embedder(self, config: dict):
        return HuggingFaceEmbeddings(
            model_name=config["embedding_model_name"],
        )


factory_map: Dict[str, Type[BaseModelFactory]] = {
    "OpenAI": OpenAIModelFactory,
    "Groq": GroqModelFactory,
    "Anthropic": AnthropicModelFactory,
    "Hugging Face": HuggingFaceModelFactory,
}


def create_models(company_name: str, config: dict) -> ModelConfig:
    factory = factory_map[company_name]()
    llm = factory.create_llm(config)
    embedder = factory.create_embedder(config)

    return ModelConfig(llm=llm, embedder=embedder)


def configure_llm(session_state: dict) -> LLMConfig:
    """Configure and return the LLM configuration settings."""
    return LLMConfig(
        model_name=session_state.get("model_name_key"),
        api_key=session_state.get("chatbot_api_key"),
        embedding_model_name=embedding_models_dict.get(
            session_state.get("model_company", None), ""
        ),
        temperature=session_state.get("temperature_key"),
        max_tokens=session_state.get("max_tokens_key"),
    )


class SentenceTransformerEmbeddings(Embeddings):
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts):
        return self.model.encode(texts, convert_to_tensor=False).tolist()

    def embed_query(self, query):
        return self.model.encode([query], convert_to_tensor=False)[0].tolist()
