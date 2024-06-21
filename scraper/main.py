"""
Application main logic
"""

import logging

import streamlit as st

from scraper.config import embedding_models_dict
from scraper.errors import CreateIndexError, QueryError
from scraper.qa import QuestionAnswering
from scraper.scraper import WebScraper
from scraper.utils import install_playwright_chromium, is_valid_url, url_exists


def start_scraping(running_placeholder: st.empty) -> None:
    """Starts the scraping task."""
    with running_placeholder:
        st.text("Running...")

    if not st.session_state.url:
        st.session_state.error_mes = "URL cannot be empty. Please enter a valid URL."
        return

    embedding_model_name = embedding_models_dict[st.session_state.language]

    try:
        install_playwright_chromium()
        qa_instance = scrape_and_process(st.session_state.url, embedding_model_name)
        st.session_state.qa = qa_instance
        st.session_state.documents = qa_instance.documents
        st.session_state.scraping_done = True
        st.session_state.error_mes = ""
    except ValueError as ve:
        st.session_state.error_mes = f"An error occurred: {ve}"
        logging.error(f"An error occurred during scraping: {ve}")
    except Exception as e:
        st.session_state.error_mes = f"An unexpected error occurred: {e}"
        logging.error(f"An unexpected error occurred during scraping: {e}")


def scrape_and_process(url: str, embedding_model_name: str) -> QuestionAnswering:
    """Scrapes the given URL and processes the documents for question answering."""
    logging.info(f"Scraping URL: {url}")
    logging.info(f"Using embedding model: {embedding_model_name}")

    if not is_valid_url(url):
        raise ValueError("Invalid URL format")
    if not url_exists(url):
        raise ValueError("The URL does not exist")

    scraper = WebScraper(url)
    documents = scraper.scrape()

    if not documents:
        logging.error("Scraper returned None for documents")
        raise ValueError("Failed to scrape documents")

    logging.info(f"Scraped {len(documents)} documents")

    qa_instance = QuestionAnswering(documents, embedding_model_name)
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
    st.session_state.question_input = None
    st.session_state.chat_history = []
    st.session_state.language_key = "english"
    st.session_state.scraping_done = False
    st.cache_data.clear()
    st.session_state.refresh_triggered = False
    st.session_state.error_mes = ""
    st.rerun()
