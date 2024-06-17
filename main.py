import logging
import os

import streamlit as st
from dotenv import load_dotenv

from scraper.config import ScraperConfig
from scraper.logging import setup_logging
from scraper.qa import QuestionAnswering
from scraper.scraper import WebScraper
from scraper.utils import is_valid_url, url_exists

load_dotenv()

HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")


def main():
    """Main function to set up the Streamlit interface and session state."""
    st.set_page_config(layout="wide")
    st.title("🕸️ Scrape Smart 🧠")

    # Initialize session state variables
    initialize_session_state()

    left_column, _, right_column = st.columns([1, 0.1, 2.6])

    with left_column:
        display_scraping_task()
        display_configuration()

    with right_column:
        display_qa_interface()

    setup_logging()


def initialize_session_state():
    """Initialize session state variables if not already set."""
    session_defaults = {
        "url": "",
        "status": [],
        "qa": None,
        "documents": [],
        "chat_history": [],
        "max_links": ScraperConfig().max_links,
        "scraping_done": False,  # Track if scraping is done
        "question_input": "",
        "refresh_triggered": False,  # Flag to trigger refresh
    }
    for key, value in session_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def display_scraping_task():
    """Display the scraping task input and controls."""
    st.header("AI-Powered Web Scraping")
    url = st.text_input(
        "Enter the URL of the website to scrape:",
        key="url_input",
        disabled=st.session_state.scraping_done,
        placeholder="http://example.com",
    )
    st.session_state.url = url
    running_placeholder = st.empty()
    st.button(
        "Start",
        on_click=lambda: start_scraping(running_placeholder),
        disabled=st.session_state.scraping_done,
    )
    st.button("Refresh", on_click=trigger_refresh)


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
        disabled=st.session_state.scraping_done,
    )
    st.warning(
        f"Up to {st.session_state.max_links} links will be scraped from the provided URL"
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
        st.session_state.scraping_done = True  # Mark scraping as done
    except Exception as e:
        st.error(f"An error occurred: {e}")
        logging.error(f"An error occurred during scraping: {e}")


def display_qa_interface():
    """Displays the QA interface for user interaction."""
    if st.session_state.scraping_done:
        chat_history_container = st.container(height=700, border=False)
        with chat_history_container:
            for role, content in st.session_state.chat_history:
                st.chat_message(role).write(content)

        chat_input_container = st.container(height=80, border=False)
        with chat_input_container:
            chat_input = st.chat_input(
                "Please ask your questions", key="question_input"
            )

        if st.session_state.qa and chat_input:
            with st.spinner("Fetching answer..."):
                answer = st.session_state.qa.query(chat_input)
                st.session_state.chat_history.append(("user", chat_input))
                st.session_state.chat_history.append(("assistant", answer))
                st.rerun()  # Re-run to display new messages


def trigger_refresh():
    """Triggers a refresh by setting the flag."""
    st.session_state.refresh_triggered = True


def clear_state():
    """Clears the session state."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state.status = []
    st.session_state.url_input = ""
    st.session_state.question_input = None
    st.session_state.chat_history = []
    st.session_state.max_links = ScraperConfig().max_links
    st.session_state.scraping_done = False
    st.cache_data.clear()
    st.session_state.refresh_triggered = False  # Reset the refresh trigger flag
    st.experimental_rerun()


if __name__ == "__main__":
    if st.session_state.get("refresh_triggered"):
        clear_state()
    main()
