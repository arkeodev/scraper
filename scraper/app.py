"""
Application main logic
"""

import logging

import streamlit as st

from scraper.config import LLMConfig, embedding_models_dict
from scraper.errors import PageScrapingError
from scraper.query.qa import WebRag
from scraper.query.sg_qa import SgRag
from scraper.scraping.sg_scraper import SgScraper
from scraper.scraping.web_scraper import WebScraper
from scraper.utils import (
    check_robots,
    install_playwright_chromium,
    is_valid_url,
    url_exists,
)


def set_error(message: str) -> None:
    """Helper function to set the session state error message."""
    st.session_state.error_mes = message


def start_scraping() -> None:
    """Starts the scraping task with improved structure and error handling."""
    url = st.session_state.get("url")
    openai_api_key = st.session_state.get("openai_key")
    model_name = st.session_state.get("model_name_key")
    temperature = st.session_state.get("temperature_key")
    max_tokens = st.session_state.get("max_tokens_key")
    embedding_model_name = embedding_models_dict[
        st.session_state.get("language_key", "english")
    ]

    if not url:
        set_error("URL cannot be empty. Please enter a valid URL.")
        return
    if not is_valid_url(url):
        set_error("Invalid URL format.")
        return
    if not url_exists(url):
        set_error("The URL does not exist.")
        return
    if not check_robots(url):
        set_error("The robots.txt file not allow to parse the URL.")
        return
    if not openai_api_key:
        set_error("Please add your OpenAI API key to continue.")
        return

    try:
        install_playwright_chromium()
        llm_config = LLMConfig(
            llm_model_name=model_name,
            embedding_model_name=embedding_model_name,
            api_key=openai_api_key,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        rag_instance = scrape_and_process(url, llm_config)
        st.session_state.update(
            {
                "qa": rag_instance,
                "scraping_done": True,
                "error_mes": "",
            }
        )
    except ValueError as ve:
        set_error(f"An error occurred: {ve}")
        logging.error(f"An error occurred during scraping: {ve}")
    except Exception as e:
        set_error(f"An unexpected error occurred: {e}")
        logging.error(
            f"An unexpected error occurred during scraping: {e}", exc_info=True
        )


def scrape_and_process(url: str, llm_config: LLMConfig) -> WebRag:
    """Scrapes the given URL and processes the documents for question answering."""
    logging.info(f"Scraping URL: {url}")
    logging.info(f"Using embedding model: {llm_config.embedding_model_name}")
    scraper = SgScraper(url)
    documents = scraper.scrape()
    if not documents:
        logging.error("Scraper returned None for documents")
        raise PageScrapingError("Failed to scrape documents")
    rag_instance = SgRag(documents, llm_config)
    return rag_instance


def trigger_refresh() -> None:
    """Triggers a refresh by setting the flag."""
    st.session_state.refresh_triggered = True
    st.rerun()


def initialize_session_state() -> None:
    """Initialize session state variables if not already set."""
    session_defaults = {
        "url": "",
        "chatbot_api_key": "",
        "model_name_key": "gpt-3.5-turbo",
        "language_key": "english",
        "temperature_key": 0.7,
        "max_tokens_key": 10_000,
        "status": [],
        "qa": None,
        "chat_history": [],
        "scraping_done": False,
        "question_input": "",
        "refresh_triggered": False,
        "error_mes": "",
    }
    for key, value in session_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def clear_state() -> None:
    """Clears the session state."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state.status = []
    st.session_state.url_input = ""
    st.session_state.chatbot_api_key = ""
    st.session_state.question_input = ""
    st.session_state.chat_history = []
    st.session_state.model_name_key = "gpt-3.5-turbo"
    st.session_state.language_key = "english"
    st.session_state.temperature_key = 0.7
    st.session_state.max_tokens_key = 10_000
    st.session_state.scraping_done = False
    st.cache_data.clear()
    st.session_state.refresh_triggered = False
    st.session_state.error_mes = ""
    st.rerun()
