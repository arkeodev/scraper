import json
from typing import List

import requests
import streamlit as st

from scraper.rag.qa import QuestionAnswering
from scraper.rag.vector_db import MilvusConfig, VectorDatabase
from scraper.scraping.robots import RobotsTxtChecker
from scraper.scraping.scraper import scrape_website


def is_valid_url(url: str) -> bool:
    """
    Checks if a given URL is valid and accessible.

    Args:
        url (str): The URL to validate.

    Returns:
        bool: True if the URL is valid, False otherwise.
    """
    try:
        result = requests.get(url)
        return result.status_code == 200
    except Exception as e:
        st.error(f"Error validating URL: {e}")
        return False


def sanitize_text(text: str) -> str:
    """
    Ensures that the text is properly encoded in UTF-8.

    Args:
        text (str): The text to sanitize.

    Returns:
        str: Sanitized text.
    """
    return text.encode("utf-8", errors="ignore").decode("utf-8", errors="ignore")


# Set page layout to wide
st.set_page_config(layout="wide")

# Streamlit app configuration
st.title("RAG-based Web Scraping and Q&A")

# Initialize session state variables
if "scraping_done" not in st.session_state:
    st.session_state.scraping_done = False
if "scraped_data" not in st.session_state:
    st.session_state.scraped_data = []
if "url" not in st.session_state:
    st.session_state.url = ""
if "show_scrape_button" not in st.session_state:
    st.session_state.show_scrape_button = False
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None
if "documents" not in st.session_state:
    st.session_state.documents = []
if "qa" not in st.session_state:
    st.session_state.qa = None

# Split the screen into three columns with specific widths
left_column, spacer, right_column = st.columns([1, 0.1, 2.6])

with left_column:
    st.header("Scraping Task")

    # URL input
    url = st.text_input(
        "Enter the URL of the website to scrape:",
        value=st.session_state.url,
        key="url_input",
    )
    st.session_state.url = url

    # Show Scrape button if URL is valid
    st.session_state.show_scrape_button = bool(url)

    # Embedding and Vector Database selections
    embedding_model = st.selectbox(
        "Select Embedding Model", ["sentence-transformers/all-MiniLM-L6-v2"]
    )

    vector_db = st.selectbox("Select Vector Database", ["Milvus"])

    # Scraping section
    if st.session_state.show_scrape_button:
        if st.button("Start Scraping"):
            if is_valid_url(url):
                robots_checker = RobotsTxtChecker(url)
                with st.spinner("Scraping..."):
                    result = scrape_website(url, robots_checker)

                if "robots.txt" in result[0]:
                    st.error(
                        "Scraping disallowed by robots.txt. Here's the content of robots.txt:"
                    )
                    st.code(result[0])
                else:
                    st.success("Scraping completed successfully.")
                    st.session_state.scraping_done = True

                    # Embed the scraped data and insert into the vector database
                    try:
                        config = MilvusConfig(
                            collection_name="document_collection",
                            embedding_model_name=embedding_model,
                        )
                        vector_db_instance = VectorDatabase(config)
                        vector_db_instance.connect_to_milvus()
                        vector_db_instance.create_or_load_collection()
                        vector_db_instance.load_embedding_model()

                        documents = [{"text": sanitize_text(text)} for text in result]

                        vector_db_instance.create_vector_store(documents)
                        st.session_state.vector_store = (
                            vector_db_instance.get_vector_store()
                        )
                        st.session_state.documents = documents

                        # Prepare QA instance
                        qa_instance = QuestionAnswering(
                            st.session_state.vector_store, documents
                        )
                        st.session_state.qa = qa_instance

                        st.success("Vector store and QA setup completed.")
                    except Exception as e:
                        st.error(f"Error creating vector store: {e}")
                        st.error(f"Exception details: {e.__class__.__name__}: {e}")
            else:
                st.error("Invalid URL. Please enter a valid URL.")

    # Clear and Restart button
    if st.button("Clear and Restart"):
        st.session_state.scraping_done = False
        st.session_state.scraped_data = []
        st.session_state.url = ""
        st.session_state.vector_store = None
        st.session_state.documents = []
        st.session_state.qa = None
        st.experimental_rerun()

with right_column:
    st.header("Question Answering")

    # Q&A section
    if st.session_state.scraping_done and st.session_state.qa:
        question = st.text_input(
            "Ask a question about the scraped data:", key="question_input"
        )
        if question:
            st.write(f"You asked: {question}")
            qa_instance = st.session_state.qa
            try:
                answer = qa_instance.answer_question(question)
                st.write(f"Answer: {answer}")
            except Exception as e:
                st.error(f"Error during question answering: {e}")
    else:
        st.text_input(
            "Ask a question about the scraped data:",
            disabled=True,
            key="question_input_disabled",
        )
