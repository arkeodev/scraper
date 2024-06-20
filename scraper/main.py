# scraper.main.py
import logging
import streamlit as st

from scraper.config import embedding_models_dict
from scraper.qa import QuestionAnswering
from scraper.scraper import WebScraper
from scraper.utils import is_valid_url, url_exists


def start_scraping(running_placeholder: st.empty):
    """Starts the scraping task."""
    with running_placeholder:
        st.text("Running...")

    if not st.session_state.url:
        st.session_state.error_mes = "URL cannot be empty. Please enter a valid URL."
        return

    embedding_model_name = embedding_models_dict[st.session_state.language]

    try:
        qa_instance = scrape_and_process(st.session_state.url, embedding_model_name)
        st.session_state.qa = qa_instance
        st.session_state.documents = qa_instance.documents
        st.session_state.scraping_done = True  # Mark scraping as done
        st.session_state.error_mes = ""  # Clear error message
    except ValueError as ve:
        st.session_state.error_mes = f"An error occurred: {ve}"
        logging.error(f"An error occurred during scraping: {ve}")
    except Exception as e:
        st.session_state.error_mes = f"An unexpected error occurred: {e}"
        logging.error(f"An unexpected error occurred during scraping: {e}")


def scrape_and_process(url: str, embedding_model_name: str) -> QuestionAnswering:
    """
    Scrapes the given URL and processes the documents for question answering.

    Args:
        url (str): The URL to scrape.
        embedding_model_name (str): The name of the embedding model to use.

    Returns:
        QuestionAnswering: An instance for question answering.
    """
    logging.info(f"Scraping URL: {url}")
    logging.info(f"Using embedding model: {embedding_model_name}")
    st.write("here1")

    if not is_valid_url(url):
        raise ValueError("Invalid URL format")
    st.write("here2")
    if not url_exists(url):
        raise ValueError("The URL does not exist")
    st.write("here3")

    scraper = WebScraper(url)
    documents = scraper.scrape()

    if documents is None:
        logging.error("Scraper returned None for documents")
        raise ValueError("Failed to scrape documents")

    logging.info(f"Scraped {len(documents)} documents")

    qa_instance = QuestionAnswering(documents, embedding_model_name)
    qa_instance.create_index()
    return qa_instance


def trigger_refresh():
    """Triggers a refresh by setting the flag."""
    st.session_state.refresh_triggered = True
    st.rerun()
