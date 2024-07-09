import logging
from collections import namedtuple
from typing import Dict, Type

from langchain_openai import OpenAIEmbeddings
from pydantic import BaseModel
from scrapegraphai.models import OpenAI

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
        # Example: return GroqLLM(config)
        pass

    def create_embedder(self, config: dict):
        # Example: return GroqEmbeddings(config)
        pass


class GoogleModelFactory(BaseModelFactory):
    def create_llm(self, config: dict):
        # Example: return GoogleLLM(config)
        pass

    def create_embedder(self, config: dict):
        # Example: return GoogleEmbeddings(config)
        pass


class OllamaModelFactory(BaseModelFactory):
    def create_llm(self, config: dict):
        # Example: return OllamaLLM(config)
        pass

    def create_embedder(self, config: dict):
        # Example: return OllamaEmbeddings(config)
        pass


class AnthropicModelFactory(BaseModelFactory):
    def create_llm(self, config: dict):
        # Example: return AnthropicLLM(config)
        pass

    def create_embedder(self, config: dict):
        # Example: return AnthropicEmbeddings(config)
        pass


class HuggingFaceModelFactory(BaseModelFactory):
    def create_llm(self, config: dict):
        # Example: return HuggingFaceLLM(config)
        pass

    def create_embedder(self, config: dict):
        # Example: return HuggingFaceEmbeddings(config)
        pass


factory_map: Dict[str, Type[BaseModelFactory]] = {
    "OpenAI": OpenAIModelFactory,
    "Groq": GroqModelFactory,
    "Google": GoogleModelFactory,
    "Ollama": OllamaModelFactory,
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
            session_state.get("language_key", "english")
        ),
        temperature=session_state.get("temperature_key"),
        max_tokens=session_state.get("max_tokens_key"),
    )
