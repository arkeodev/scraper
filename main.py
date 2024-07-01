"""
Main application
"""

from typing import List

import streamlit as st

from scraper.app import initiate_scraping_process
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


def load_css():
    """Load CSS styles from a css file."""
    with open(".css/app_styles.css", "r") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def display_title() -> None:
    """Display title and image."""
    # Use a container to wrap the image for specific styling
    st.markdown("<h1>m o l e</h1>", unsafe_allow_html=True)
    st.image("scraper/images/mole.png")
    st.markdown("<h2>AI powered web scraping</h2>", unsafe_allow_html=True)


def display_scraping_ui() -> None:
    """Display scraping interface."""

    # Task selection using a select box
    task_options = {
        "Parse the URL text": display_url_input,
        "Parse PDF file(s)": display_file_uploader,
    }

    task_selection = st.selectbox(
        "Select Task",
        options=list(task_options.keys()),
        placeholder="Select task...",
        index=0,
        key="task_key",
        disabled=st.session_state.scraping_done,
    )

    # Execute the corresponding function based on task selection
    task_options[task_selection]()

    # Display error messages if any
    if st.session_state.error_mes:
        st.error(f"{st.session_state.error_mes}")

    # Layout for start and refresh buttons
    start_col, refresh_col = st.columns([1, 1], gap="small")

    with start_col:
        st.button(
            "Start",
            on_click=lambda: initiate_scraping_process(st.session_state),
            key="start_button",
            disabled=st.session_state.scraping_done,
        )

    with refresh_col:
        st.button("Refresh", key="refresh_button", on_click=trigger_refresh)


def display_url_input():
    """Display URL input field."""
    st.session_state.source = st.text_input(
        "Enter the URL of the website to scrape:",
        key="url_input",
        placeholder="http://example.com",
        disabled=st.session_state.scraping_done,
    )
    st.session_state.input_type = "url"


def display_file_uploader():
    """Display file uploader for PDF files."""
    st.session_state.source = st.file_uploader(
        "Choose a PDF file to parse",
        type=["pdf"],
        disabled=st.session_state.scraping_done,
    )
    st.session_state.input_type = "pdf"


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
    st.session_state.model_name = st.selectbox(
        "Select the Model:",
        options=("gpt-3.5-turbo", "gpt-4o", "gpt-4", "gpt-4-turbo"),
        placeholder="Select model...",
        index=0,
        key="model_name_key",
        disabled=st.session_state.scraping_done,
    )
    st.session_state.openai_key = st.text_input(
        "OpenAI API Key",
        key="chatbot_api_key",
        type="password",
        disabled=st.session_state.scraping_done,
    )
    st.session_state.temperature = st.slider(
        "Temperature",
        0.0,
        1.0,
        0.7,
        key="temperature_key",
        disabled=st.session_state.scraping_done,
    )
    st.session_state.max_tokens = st.number_input(
        "Max Tokens",
        min_value=1,
        value=1000,
        key="max_tokens_key",
        disabled=st.session_state.scraping_done,
    )


def display_qa_ui() -> None:
    """Displays the QA interface for user interaction."""
    if st.session_state.scraping_done:
        user_input = st.chat_input("Please ask your questions", key="question_input")
        if user_input:
            handle_submit(user_input)


def handle_submit(user_input: str):
    """Handle the submission of the chat input."""
    with st.spinner("Fetching answer..."):
        answer = st.session_state.qa.execute(user_input)
        if not answer:
            answer = "I'm sorry, I don't answer this question."
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


def trigger_refresh() -> None:
    """Triggers a refresh by setting the flag."""
    st.session_state.refresh_triggered = True
    st.rerun()


def initialize_session_state() -> None:
    """Initialize session state variables if not already set."""
    session_defaults = {
        "url": "",
        "chatbot_api_key": "",
        "model_name_key": "gpt-3.5-turbo",
        "language_key": "english",
        "temperature_key": 0.7,
        "max_tokens_key": 1000,
        "status": [],
        "qa": None,
        "chat_history": [],
        "scraping_done": False,
        "question_input": "",
        "refresh_triggered": False,
        "error_mes": "",
    }
    for key, value in session_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def clear_state() -> None:
    """Clears the session state."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state.status = []
    st.session_state.url_input = ""
    st.session_state.chatbot_api_key = ""
    st.session_state.question_input = ""
    st.session_state.chat_history = []
    st.session_state.model_name_key = "gpt-3.5-turbo"
    st.session_state.language_key = "english"
    st.session_state.temperature_key = 0.7
    st.session_state.max_tokens_key = 1000
    st.session_state.scraping_done = False
    st.cache_data.clear()
    st.session_state.refresh_triggered = False
    st.session_state.error_mes = ""
    st.rerun()


if __name__ == "__main__":
    if st.session_state.get("refresh_triggered"):
        clear_state()
    main()
