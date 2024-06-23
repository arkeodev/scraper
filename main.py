"""
Main application
"""

import base64

import streamlit as st

from scraper.app import (
    clear_state,
    initialize_session_state,
    start_scraping,
    trigger_refresh,
)
from scraper.logging import setup_logging


def main():
    """Main function to set up the Streamlit interface and session state."""
    st.set_page_config(layout="wide")

    # Load CSS styles
    load_css()

    # Initialize session state variables
    initialize_session_state()

    # Set up three columns, using st.columns
    left_column, _, right_column = st.columns([1, 0.1, 2.6])

    with left_column:
        # Use a container to wrap the image for specific styling
        container = st.container()
        container.markdown("<h1>m o l e</h1>", unsafe_allow_html=True)
        container.image("scraper/images/mole.png")
        container.markdown("<h2>AI powered web scraping</h2>", unsafe_allow_html=True)

        display_scraping_ui()
        with st.expander("Configuration", expanded=True):
            display_config_ui()
        # Add a space and then the GitHub link at the bottom
        st.markdown(" ")  # This adds a bit of space
        # Add styled GitHub link at the bottom
        st.markdown(
            "<a class='github-link' href='https://github.com/arkeodev/scraper' target='_blank'>"
            "<span class='github-icon'></span>View on GitHub</a>",
            unsafe_allow_html=True,
        )

    with right_column:
        display_qa_ui()

    setup_logging()


def display_config_ui() -> None:
    """Display configuration options for the scraper."""
    st.session_state.language = st.selectbox(
        "Select the Language of the Web Site:",
        options=("english", "turkish"),
        placeholder="Select language...",
        index=0,
        key="language_key",
        disabled=st.session_state.scraping_done,
    )


def display_scraping_ui() -> None:
    """Display scraping interface."""
    url = st.text_input(
        "Enter the URL of the website to scrape:",
        key="url_input",
        placeholder="http://example.com",
    )
    st.session_state.url = url
    running_placeholder = st.empty()
    if st.session_state.error_mes:
        st.error(f"{st.session_state.error_mes}")
    st.button("Start", on_click=lambda: start_scraping(running_placeholder))
    st.button("Refresh", on_click=trigger_refresh)


def display_qa_ui() -> None:
    """Displays the QA interface for user interaction."""
    if st.session_state.scraping_done:
        chat_input = st.text_input("Please ask your questions", key="question_input")
        if chat_input:
            with st.spinner("Fetching answer..."):
                answer = st.session_state.qa.query(chat_input)
                st.session_state.chat_history.append(("assistant", answer))
                st.session_state.chat_history.append(("user", chat_input))

        # Reverse the list to display the latest message first
        reversed_chat_history = reversed(st.session_state.chat_history)
        for role, content in reversed_chat_history:
            st.markdown(
                f"<div class='chat-message-{role}'>{content}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(" ")


def load_css():
    """Load CSS styles from a css file."""
    with open(".css/app_styles.css", "r") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


if __name__ == "__main__":
    if st.session_state.get("refresh_triggered"):
        clear_state()
    main()
