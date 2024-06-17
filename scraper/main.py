import logging

import streamlit as st

from scraper.config import ScraperConfig
from scraper.qa import QuestionAnswering
from scraper.scraper import WebScraper
from scraper.utils import is_valid_url, url_exists


def start_scraping(running_placeholder: st.empty):
    """Starts the scraping task."""
    with running_placeholder:
        st.text("Running...")

    scraper_config = ScraperConfig(max_links=st.session_state.max_links)

    try:
        qa_instance = scrape_and_process(st.session_state.url, scraper_config)
        st.session_state.qa = qa_instance
        st.session_state.documents = qa_instance.documents
        st.session_state.scraping_done = True  # Mark scraping as done
    except Exception as e:
        st.error(f"An error occurred: {e}")
        logging.error(f"An error occurred during scraping: {e}")


def scrape_and_process(url: str, config: ScraperConfig) -> QuestionAnswering:
    """
    Scrapes the given URL and processes the documents for question answering.

    Args:
        url (str): The URL to scrape.
        config (ScraperConfig): Configuration for the scraper.

    Returns:
        QuestionAnswering: An instance for question answering.
    """
    if not is_valid_url(url):
        raise ValueError("Invalid URL format")
    if not url_exists(url):
        raise ValueError("The URL does not exist")

    scraper = WebScraper(url)
    documents = scraper.scrape()
    qa_instance = QuestionAnswering(documents)
    qa_instance.create_index()
    return qa_instance


def trigger_refresh():
    """Triggers a refresh by setting the flag."""
    st.session_state.refresh_triggered = True
