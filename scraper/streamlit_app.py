import logging
from urllib.parse import urlparse

import requests
import streamlit as st
from sentence_transformers import SentenceTransformer

from scraper.config.config import QAConfig, ScraperConfig
from scraper.config.logging import safe_run, setup_logging
from scraper.rag.qa import QuestionAnswering
from scraper.rag.vector_db import VectorDatabase
from scraper.scraping.scraper import WebScraper
from scraper.utility.utils import generate_collection_name

setup_logging()  # Initialize logging at the start of your app


def main():
    st.set_page_config(layout="wide")
    st.title("Web Scraping and Q&A")

    # Streamlit session state initialization
    if "url" not in st.session_state:
        st.session_state.url = ""
    if "status" not in st.session_state:
        st.session_state.status = []
    if "qa" not in st.session_state:
        st.session_state.qa = None

    left_column, _, right_column = st.columns([1, 0.1, 2.6])

    with left_column:
        st.header("Scraping Task")
        url = st.text_input("Enter the URL of the website to scrape:", key="url_input")
        st.session_state.url = url
        scrape_button = st.button("Start Scraping", on_click=scrape_and_process)

        st.header("Configuration")
        st.session_state.max_links = st.number_input(
            "Max Links to Scrape:", min_value=1, value=2, key="max_links_key"
        )
        st.warning(
            f"Max {st.session_state.max_links} links will be scraped from the provided URL"
        )
        st.session_state.page_load_timeout = st.number_input(
            "Page Load Timeout (seconds):",
            min_value=1,
            value=15,
            key="page_load_timeout_key",
        )
        st.session_state.page_load_sleep = st.number_input(
            "Page Load Sleep (seconds):",
            min_value=1,
            value=5,
            key="page_load_sleep_key",
        )
        st.session_state.top_n_chunks = st.number_input(
            "Top N Chunks for QA:", min_value=1, value=5, key="top_n_chunks_key"
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
            for status in st.session_state.status:
                status_container.write(status)


@safe_run
def scrape_and_process():
    """Handles the scraping and processing of the website data."""
    if st.session_state.url:
        if not is_valid_url(st.session_state.url):
            st.error("Invalid URL format. Please enter a valid URL.")
            return

        if not url_exists(st.session_state.url):
            st.error("The URL does not exist. Please enter a valid URL.")
            return

        st.session_state.status = []
        status_container = st.empty()

        scraper_config = ScraperConfig(
            max_links=st.session_state.max_links,
            page_load_timeout=st.session_state.page_load_timeout,
            page_load_sleep=st.session_state.page_load_sleep,
        )

        scraper = WebScraper(
            st.session_state.url,
            lambda message: update_progress(message, status_container),
            config=scraper_config,
        )
        documents = scraper.scrape()
        if documents:
            formatted_documents = [{"text": doc} for doc in documents]
            process_documents(formatted_documents)


def is_valid_url(url: str) -> bool:
    """Checks if the URL is in a valid format."""
    parsed = urlparse(url)
    return bool(parsed.scheme) and bool(parsed.netloc)


def url_exists(url: str) -> bool:
    """Checks if the URL exists by making a HEAD request."""
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False


@safe_run
@st.cache_data
def process_documents(documents):
    """Processes documents and sets up the vector database and QA system."""
    qa_config = QAConfig(top_n_chunks=st.session_state.top_n_chunks)

    vector_db_instance = VectorDatabase(st.session_state.url)
    vector_db_instance.connect_to_milvus()
    vector_db_instance.create_vector_store()
    vector_db_instance.insert_documents(documents)
    st.session_state.vector_store = vector_db_instance.get_vector_store()
    st.session_state.documents = documents

    # Prepare QA instance
    qa_instance = QuestionAnswering(
        st.session_state.vector_store, documents, qa_config=qa_config
    )
    st.session_state.qa = qa_instance

    st.success("Vector store and QA setup completed.")


def display_qa_interface():
    """Displays the QA interface for user interaction."""
    if st.session_state.qa:
        question = st.text_input("Enter your question:", key="question_input")
        if st.button("Get Answer"):
            if question:
                with st.spinner("Fetching answer..."):
                    answer = st.session_state.qa.answer_question(question)
                    st.write(f"**Answer:** {answer}")
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
    st.session_state.max_links_key = ScraperConfig().max_links
    st.session_state.page_load_timeout_key = ScraperConfig().page_load_timeout
    st.session_state.page_load_sleep_key = ScraperConfig().page_load_sleep
    st.session_state.top_n_chunks_key = QAConfig().top_n_chunks
    st.cache_data.clear()
    st.experimental_rerun()


def update_progress(message, status_container):
    st.session_state.status.append(message)
    with status_container.container():
        for status in st.session_state.status:
            st.write(status)


if __name__ == "__main__":
    main()
