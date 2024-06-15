"""
Streamlit application for web scraping and question answering.
"""

import logging
import os
from typing import List

import streamlit as st
from dotenv import load_dotenv

from scraper.config.config import QAConfig, ScraperConfig
from scraper.config.logging import setup_logging
from scraper.rag.qa import QuestionAnswering
from scraper.scraping.scraper import WebScraper
from scraper.utility.utils import is_valid_url, url_exists

load_dotenv()

HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")


def main():
    """Main function to set up the Streamlit interface and session state."""
    st.set_page_config(layout="wide")
    st.title("Web Scraping and Q&A")

    # Initialize session state variables
    initialize_session_state()

    left_column, _, right_column = st.columns([1, 0.1, 2.6])

    with left_column:
        display_scraping_task()
        display_configuration()

    with right_column:
        qa_container = st.container()

        with qa_container:
            st.header("Question Answering")
            display_qa_interface()

    setup_logging()


def initialize_session_state():
    """Initialize session state variables if not already set."""
    session_defaults = {
        "url": "",
        "status": [],
        "qa": None,
        "vector_store": None,
        "documents": [],
        "max_links": ScraperConfig().max_links,
    }
    for key, value in session_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def display_scraping_task():
    """Display the scraping task input and controls."""
    st.header("Scraping Task")
    url = st.text_input("Enter the URL of the website to scrape:", key="url_input")
    st.session_state.url = url
    running_placeholder = st.empty()
    st.button("Start", on_click=lambda: start_scraping(running_placeholder))

    if st.button("Clear"):
        clear_state()


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


def display_configuration():
    """Display configuration options for the scraper."""
    st.header("Configuration")
    st.session_state.max_links = st.number_input(
        "Max Links to Scrape:",
        min_value=1,
        value=st.session_state.max_links,
        key="max_links_key",
    )
    st.warning(
        f"Max {st.session_state.max_links} links will be scraped from the provided URL"
    )


def start_scraping(running_placeholder):
    """Starts the scraping task."""
    with running_placeholder:
        st.text("Running...")

    scraper_config = ScraperConfig(max_links=st.session_state.max_links)

    try:
        qa_instance = scrape_and_process(st.session_state.url, scraper_config)
        st.session_state.qa = qa_instance
        st.session_state.documents = qa_instance.documents
    except Exception as e:
        st.error(f"An error occurred: {e}")
        logging.error(f"An error occurred during scraping: {e}")


def display_qa_interface():
    """Displays the QA interface for user interaction."""
    if st.session_state.qa:
        question = st.text_input("Enter your question:", key="question_input")
        if st.button("Get Answer"):
            if question:
                with st.spinner("Fetching answer..."):
                    try:
                        st.write(f"**Asking question:** {question}")
                        answer = st.session_state.qa.query(question)
                        st.write(f"**Answer:** {answer}")
                    except Exception as e:
                        st.error(f"Error fetching answer: {e}")
                        logging.error(f"Error fetching answer: {e}")
            else:
                st.warning("Please enter a question.")
    else:
        st.info("Please perform scraping and processing first.")


def clear_state():
    """Clears the session state."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state.status = []
    st.session_state.url_input = ""
    st.session_state.question_input = None
    st.session_state.max_links = ScraperConfig().max_links
    st.cache_data.clear()
    st.experimental_rerun()


if __name__ == "__main__":
    main()
