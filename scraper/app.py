"""
Application main logic
"""

import logging

import streamlit as st

from scraper.config import embedding_models_dict
from scraper.errors import PageScrapingError
from scraper.qa import QuestionAnswering
from scraper.scraper import WebScraper
from scraper.utils import install_playwright_chromium, is_valid_url, url_exists


def set_error(message: str) -> None:
    """Helper function to set the session state error message."""
    st.session_state.error_mes = message


def start_scraping() -> None:
    """Starts the scraping task with improved structure and error handling."""
    url = st.session_state.get("url")
    openai_key = st.session_state.get("openai_key")

    if not url:
        set_error("URL cannot be empty. Please enter a valid URL.")
        return
    if not is_valid_url(url):
        set_error("Invalid URL format")
        return
    if not url_exists(url):
        set_error("The URL does not exist")
        return
    if not openai_key:
        set_error("Please add your OpenAI API key to continue.")
        return

    embedding_model_name = embedding_models_dict[
        st.session_state.get("language", "default_language")
    ]

    try:
        install_playwright_chromium()
        qa_instance = scrape_and_process(url, embedding_model_name, openai_key)
        st.session_state.update(
            {
                "qa": qa_instance,
                "documents": qa_instance.documents,
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


def scrape_and_process(
    url: str, embedding_model_name: str, open_ai_key: str
) -> QuestionAnswering:
    """Scrapes the given URL and processes the documents for question answering."""
    logging.info(f"Scraping URL: {url}")
    logging.info(f"Using embedding model: {embedding_model_name}")

    scraper = WebScraper(url)
    documents = scraper.scrape()
    if not documents:
        logging.error("Scraper returned None for documents")
        raise PageScrapingError("Failed to scrape documents")
    logging.info(f"Scraped {len(documents)} documents")

    qa_instance = QuestionAnswering(documents, embedding_model_name, open_ai_key)
    qa_instance.create_index()
    return qa_instance


def trigger_refresh() -> None:
    """Triggers a refresh by setting the flag."""
    st.session_state.refresh_triggered = True
    st.rerun()


def initialize_session_state() -> None:
    """Initialize session state variables if not already set."""
    session_defaults = {
        "url": "",
        "chatbot_api_key": "",
        "status": [],
        "qa": None,
        "documents": [],
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
    st.session_state.language_key = "english"
    st.session_state.scraping_done = False
    st.cache_data.clear()
    st.session_state.refresh_triggered = False
    st.session_state.error_mes = ""
    st.rerun()
