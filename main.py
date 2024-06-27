"""
Main application
"""

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
        display_title()
        display_scraping_ui()
        with st.expander("Configuration", expanded=False):
            display_config_ui()
        st.markdown(" ")
        # Add styled GitHub link at the bottom
        st.markdown(
            "<a class='github-link' href='https://github.com/arkeodev/scraper' target='_blank'>"
            "<span class='github-icon'></span>View on GitHub</a>",
            unsafe_allow_html=True,
        )

    with right_column:
        display_qa_ui()

    setup_logging()


def display_title() -> None:
    """Display title and image."""
    # Use a container to wrap the image for specific styling
    st.markdown("<h1>m o l e</h1>", unsafe_allow_html=True)
    st.image("scraper/images/mole.png")
    st.markdown("<h2>AI powered web scraping</h2>", unsafe_allow_html=True)


def display_config_ui() -> None:
    """Display configuration options for the scraper."""
    # Task selection
    st.task_name = st.selectbox(
        "Select Task",
        options=[
            "Parse the URL text and ask questions to answer",
        ],
        placeholder="Select task...",
        index=0,
        key="task_key",
        disabled=st.session_state.scraping_done,
    )
    st.session_state.language = st.selectbox(
        "Select the Language of the Web Site:",
        options=("english", "turkish"),
        placeholder="Select language...",
        index=0,
        key="language_key",
        disabled=st.session_state.scraping_done,
    )
    st.session_state.model_name = st.selectbox(
        "Select the Model:",
        options=("gpt-3.5-turbo", "gpt-4o", "gpt-4", "gpt-4-turbo"),
        placeholder="Select model...",
        index=0,
        key="model_name_key",
        disabled=st.session_state.scraping_done,
    )
    st.session_state.openai_key = st.text_input(
        "OpenAI API Key", key="chatbot_api_key", type="password"
    )
    st.session_state.temperature = st.slider(
        "Temperature", 0.0, 1.0, 0.7, key="temperature_key"
    )
    st.session_state.max_tokens = st.number_input(
        "Max Tokens", min_value=1, value=100, key="max_tokens_key"
    )


def display_scraping_ui() -> None:
    """Display scraping interface."""
    st.session_state.url = st.text_input(
        "Enter the URL of the website to scrape:",
        key="url_input",
        placeholder="http://example.com",
    )
    if st.session_state.error_mes:
        st.error(f"{st.session_state.error_mes}")
    st.button(
        "Start",
        on_click=lambda: start_scraping(),
        disabled=st.session_state.scraping_done,
    )
    st.button("Refresh", on_click=trigger_refresh)


def handle_submit(user_input: str):
    """Handle the submission of the chat input."""
    with st.spinner("Fetching answer..."):
        context = st.session_state.qa.rag(user_input)
        answer = st.session_state.qa.query(context)
        st.session_state.chat_history.append(("assistant", answer))
        st.session_state.chat_history.append(("user", user_input))

        # Reverse the list to display the latest message first
        reversed_chat_history = reversed(st.session_state.chat_history)
        for role, content in reversed_chat_history:
            st.markdown(
                f"<div class='chat-message-{role}'>{content}</div>",
                unsafe_allow_html=True,
            )
        st.markdown(" ")


def display_qa_ui() -> None:
    """Displays the QA interface for user interaction."""
    if st.session_state.scraping_done:
        user_input = st.chat_input("Please ask your questions", key="question_input")
        if user_input:
            handle_submit(user_input)


def load_css():
    """Load CSS styles from a css file."""
    with open(".css/app_styles.css", "r") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


if __name__ == "__main__":
    if st.session_state.get("refresh_triggered"):
        clear_state()
    main()
