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


# Streamlit app configuration
st.title("RAG-based Web Scraping and Q&A")

# Session state to manage the scraping state
if "scraping_done" not in st.session_state:
    st.session_state.scraping_done = False
if "scraped_data" not in st.session_state:
    st.session_state.scraped_data = []

# URL input
url = st.text_input("Enter the URL of the website to scrape:")

# Scraping section
if url and st.button("Start Scraping"):
    if is_valid_url(url):
        st.write(f"Scraping URL: {url}")
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
    st.experimental_rerun()

# Q&A section
if st.session_state.scraping_done:
    question = st.text_input("Ask a question about the scraped data:")
    if question:
        st.write(f"You asked: {question}")
        # Here you can add your Q&A logic to process the question
