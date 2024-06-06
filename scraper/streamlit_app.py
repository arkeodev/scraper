import json
import os

import requests
import streamlit as st
from scraping.robots import RobotsTxtChecker
from scraping.scraper import scrape_website

from scraper.database.vector_db import VectorDatabase
from scraper.qa.qa import QuestionAnswering


def is_valid_url(url: str) -> bool:
    try:
        result = requests.get(url)
        return result.status_code == 200
    except Exception as e:
        st.error(f"Error validating URL: {e}")
        return False


# Set page layout to wide
st.set_page_config(layout="wide")

# Streamlit app configuration
st.title("RAG-based Web Scraping and Q&A")

# Session state to manage the scraping state
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

# Debug: Print current session state
st.write("Current session state before:", st.session_state)

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
    if url:
        st.session_state.show_scrape_button = True
    else:
        st.session_state.show_scrape_button = False

    # Embedding and Vector Database selections
    embedding_model = st.selectbox(
        "Select Embedding Model", ["sentence-transformers/all-MiniLM-L6-v2"]
    )

    vector_db = st.selectbox("Select Vector Database", ["FAISS"])

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
                    st.json(json.dumps(result, indent=2))
                    st.session_state.scraping_done = True
                    st.session_state.scraped_data = result

                    # Debug: Scraped data
                    st.write("Scraped data:", st.session_state.scraped_data)

                    # Embed the scraped data and insert into the vector database
                    try:
                        st.write("AAAAAAAAAAA")
                        vector_db_instance = VectorDatabase(embedding_model, vector_db)
                        st.write("BBBBBBBBBB")
                        documents = [{"text": text} for text in result]
                        vector_db_instance.create_vector_store(documents)
                        st.session_state.vector_store = (
                            vector_db_instance.get_vector_store()
                        )
                        st.session_state.documents = documents

                        # Debug: Vector store and documents
                        st.write("Vector store created:", st.session_state.vector_store)
                        st.write("Documents stored:", st.session_state.documents)

                    except Exception as e:
                        st.error(f"Error creating vector store: {e}")
            else:
                st.error("Invalid URL. Please enter a valid URL.")

    # Clear and Restart button
    if st.button("Clear and Restart"):
        st.session_state.scraping_done = False
        st.session_state.scraped_data = []
        st.session_state.url = ""
        st.session_state.vector_store = None
        st.session_state.documents = []
        st.experimental_rerun()

with right_column:
    st.header("Question Answering")

    # Q&A section
    if st.session_state.scraping_done:
        question = st.text_input(
            "Ask a question about the scraped data:", key="question_input"
        )
        if question:
            st.write(f"You asked: {question}")

            # Debug: Check vector store and documents
            st.write("Vector store:", st.session_state.vector_store)
            st.write("Documents:", st.session_state.documents)

            # Using the free LLM to answer the question
            if st.session_state.vector_store:
                qa_instance = QuestionAnswering(st.session_state.vector_store)
                try:
                    answer = qa_instance.answer_question(
                        question, st.session_state.documents
                    )
                    st.write(f"Answer: {answer}")
                except Exception as e:
                    st.error(f"Error during question answering: {e}")
    else:
        st.text_input(
            "Ask a question about the scraped data:",
            disabled=True,
            key="question_input_disabled",
        )

# Debug: Print current session state after
st.write("Current session state after:", st.session_state)
