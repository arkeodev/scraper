import json

import requests
import streamlit as st
from scraping.robots import RobotsTxtChecker
from scraping.scraper import scrape_website


def is_valid_url(url: str) -> bool:
    try:
        result = requests.get(url)
        return result.status_code == 200
    except:
        return False


# Set page layout to wide
st.set_page_config(layout="wide")

# Streamlit app configuration
st.title("RAG-based Web Scraping")

# Session state to manage the scraping state
if "scraping_done" not in st.session_state:
    st.session_state.scraping_done = False
if "scraped_data" not in st.session_state:
    st.session_state.scraped_data = []
if "url" not in st.session_state:
    st.session_state.url = ""
if "show_scrape_button" not in st.session_state:
    st.session_state.show_scrape_button = False

# Split the screen into three columns with specific widths
left_column, spacer, right_column = st.columns([1, 0.1, 2.6])

with left_column:
    st.header("Scraping Task")

    # URL input
    url = st.text_input(
        "Enter the URL of the website to scrape:",
        value=st.session_state.url,
        key="url_input",
        on_change=lambda: st.session_state.update(show_scrape_button=True),
    )
    st.session_state.url = url

    # Scraping section
    if st.session_state.show_scrape_button and url:
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
            else:
                st.error("Invalid URL. Please enter a valid URL.")

    # Clear and Restart button
    if st.button("Clear and Restart"):
        st.session_state.scraping_done = False
        st.session_state.scraped_data = []
        st.session_state.url = ""
        st.session_state.show_scrape_button = False
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
            # Here you can add your Q&A logic to process the question
    else:
        st.text_input(
            "Ask a question about the scraped data:",
            disabled=True,
            key="question_input_disabled",
        )
