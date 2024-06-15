# streamlit_app.py
import streamlit as st

from scraper.app.app import ScraperApp
from scraper.config.config import QAConfig, ScraperConfig
from scraper.config.logging import setup_logging


def main():
    st.set_page_config(layout="wide")
    st.title("Web Scraping and Q&A")

    # Initialize session state variables
    if "url" not in st.session_state:
        st.session_state.url = ""
    if "status" not in st.session_state:
        st.session_state.status = []
    if "qa" not in st.session_state:
        st.session_state.qa = None
    if "vector_store" not in st.session_state:
        st.session_state.vector_store = None
    if "documents" not in st.session_state:
        st.session_state.documents = []

    if "max_links" not in st.session_state:
        st.session_state.max_links = ScraperConfig().max_links
    if "page_load_timeout" not in st.session_state:
        st.session_state.page_load_timeout = ScraperConfig().page_load_timeout
    if "page_load_sleep" not in st.session_state:
        st.session_state.page_load_sleep = ScraperConfig().page_load_sleep
    if "top_n_chunks" not in st.session_state:
        st.session_state.top_n_chunks = QAConfig().top_n_chunks

    left_column, _, right_column = st.columns([1, 0.1, 2.6])

    with left_column:
        st.header("Scraping Task")
        url = st.text_input("Enter the URL of the website to scrape:", key="url_input")
        st.session_state.url = url
        running_placeholder = st.empty()
        scrape_button = st.button(
            "Start", on_click=lambda: start_scraping(running_placeholder)
        )

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
        st.session_state.page_load_timeout = st.number_input(
            "Page Load Timeout (seconds):",
            min_value=1,
            value=st.session_state.page_load_timeout,
            key="page_load_timeout_key",
        )
        st.session_state.page_load_sleep = st.number_input(
            "Page Load Sleep (seconds):",
            min_value=1,
            value=st.session_state.page_load_sleep,
            key="page_load_sleep_key",
        )
        st.session_state.top_n_chunks = st.number_input(
            "Top N Chunks for QA:",
            min_value=1,
            value=st.session_state.top_n_chunks,
            key="top_n_chunks_key",
        )

        if st.button("Clear"):
            clear_state()

    with right_column:
        qa_container = st.container()
        separator = st.container()
        progress_container = st.container()

        with qa_container:
            st.header("Question Answering")
            display_qa_interface()

        with separator:
            st.write(" ")

        with progress_container:
            st.header("Scraping Progress")
            status_container = st.empty()
            if "status" in st.session_state:
                for status in st.session_state.status:
                    status_container.write(status)

    setup_logging(
        log_container=progress_container
    )  # Initialize logging with the Streamlit log container


def start_scraping(running_placeholder):
    """Starts the scraping task"""
    with running_placeholder:
        st.text("Running...")

    scraper_config = ScraperConfig(
        max_links=st.session_state.max_links,
        page_load_timeout=st.session_state.page_load_timeout,
        page_load_sleep=st.session_state.page_load_sleep,
    )
    scraper_app = ScraperApp(scraper_config)

    try:
        qa_instance = scraper_app.scrape_and_process(st.session_state.url)
        st.session_state.qa = qa_instance
        st.session_state.documents = qa_instance.documents
    except Exception as e:
        st.error(f"An error occurred: {e}")


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
    st.session_state.page_load_timeout = ScraperConfig().page_load_timeout
    st.session_state.page_load_sleep = ScraperConfig().page_load_sleep
    st.session_state.top_n_chunks = QAConfig().top_n_chunks
    st.cache_data.clear()
    st.experimental_rerun()


if __name__ == "__main__":
    main()
