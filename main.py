"""
Main application
"""

from typing import List

import streamlit as st

from scraper.app import execute_scraping
from scraper.config import tasks
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
    st.image("images/mole.png")
    st.markdown("<h2>AI powered web scraping</h2>", unsafe_allow_html=True)


def display_scraping_ui() -> None:
    """Display scraping interface."""

    # Create a dictionary to map source definitions to task instances
    source_options = {task.source_def: task for task in tasks}
    source_selection = st.selectbox(
        "Select Source",
        options=list(source_options.keys()),
        placeholder="Select source...",
        index=0,
        key="source_key",
        disabled=st.session_state.scraping_done,
    )
    selected_source = source_options[source_selection]
    st.session_state.selected_source = selected_source

    # Execute the corresponding function based on task selection
    if selected_source.is_url:
        display_url_input()
    else:
        display_file_uploader(selected_source.allowed_extensions)

    # Display task selection and update session state with the selected task.
    selected_task = st.selectbox(
        "Select Task",
        options=selected_source.task_def,
        placeholder="Select task...",
        index=0,
        key="task_key",
        disabled=st.session_state.scraping_done,
    )
    st.session_state.selected_task_index = selected_source.task_def.index(selected_task)

    # Display error messages if any
    if st.session_state.error_mes:
        st.error(f"{st.session_state.error_mes}")

    # Layout for start and refresh buttons
    start_col, refresh_col = st.columns([1, 1], gap="small")

    with start_col:
        st.button(
            "Start",
            on_click=lambda: execute_scraping(st.session_state),
            key="start_button",
            disabled=st.session_state.scraping_done,
        )

    with refresh_col:
        st.button("Refresh", key="refresh_button", on_click=trigger_refresh)


def display_file_uploader(allowed_extensions: List[str]):
    """Display file uploader for parsing files."""
    st.session_state.source = st.file_uploader(
        "Choose a file to parse",
        type=allowed_extensions,
        disabled=st.session_state.scraping_done,
    )


def display_url_input():
    """Display URL input field."""
    st.session_state.source = st.text_input(
        "Enter the URL of the website to scrape:",
        key="url_input",
        placeholder="http://example.com",
        disabled=st.session_state.scraping_done,
    )


def display_config_ui() -> None:
    """Display configuration options for the scraper."""
    st.session_state.model_company = st.selectbox(
        "Select the Model Company:",
        options=("OpenAI", "Groq", "Anthropic", "Hugging Face"),
        placeholder="Select model company...",
        index=0,
        key="model_company_key",
        disabled=st.session_state.scraping_done,
    )
    # Load dynamic configuration options based on the selected company
    load_model_specific_ui(st.session_state.model_company)


def load_model_specific_ui(company_name: str):
    """Load UI components based on model company."""
    if company_name == "OpenAI":
        st.session_state.model_name = st.selectbox(
            "Select the Model:",
            options=("gpt-4o-mini", "gpt-4o", "gpt-4", "gpt-4-turbo"),
            placeholder="Select model...",
            index=0,
            key="model_name_key",
            disabled=st.session_state.scraping_done,
        )
        st.session_state.api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            key="chatbot_api_key",
            disabled=st.session_state.scraping_done,
        )
    elif company_name == "Anthropic":
        st.session_state.model_name = st.selectbox(
            "Select the Model:",
            options=("claude-3-haiku-20240307", "claude-3-5-sonnet-20240620"),
            placeholder="Select model...",
            index=0,
            key="model_name_key",
            disabled=st.session_state.scraping_done,
        )
        st.session_state.api_key = st.text_input(
            "Antrophic API Key",
            type="password",
            key="chatbot_api_key",
            disabled=st.session_state.scraping_done,
        )
    elif company_name == "Groq":
        st.session_state.model_name = st.selectbox(
            "Select the Model:",
            options=(
                "llama3-8b-8192",
                "llama3-70b-8192",
                "mixtral-8x7b-32768",
                "gemma-7b-it",
                "gemma2-9b-it",
            ),
            placeholder="Select model...",
            index=0,
            key="model_name_key",
            disabled=st.session_state.scraping_done,
        )
        st.session_state.api_key = st.text_input(
            "Groq API Key",
            type="password",
            key="chatbot_api_key",
            disabled=st.session_state.scraping_done,
        )
    elif company_name == "Hugging Face":
        st.session_state.model_name = st.selectbox(
            "Select the Model:",
            options=(
                "mistralai/Mistral-7B-Instruct-v0.3",
                "meta-llama/Meta-Llama-3-8B-Instruct",
            ),
            placeholder="Select model...",
            index=0,
            key="model_name_key",
            disabled=st.session_state.scraping_done,
        )
        st.session_state.api_key = st.text_input(
            "Hugging Face API Key",
            type="password",
            key="chatbot_api_key",
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
        if st.session_state.selected_task_index == 0:
            user_input = st.chat_input(
                "Please ask your questions", key="question_input"
            )
            if user_input:
                handle_submit(user_input)
        elif st.session_state.selected_task_index == 1:
            handle_summary_submit()
        elif st.session_state.selected_task_index == 2:
            handle_keypoints_submit()


def handle_submit(user_input: str):
    """Handle the submission of the chat input."""
    with st.spinner("Fetching answer..."):
        graph = st.session_state.graph
        answer = graph.execute(user_input)
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


def handle_summary_submit():
    """Handle the submission for document summarization."""
    with st.spinner("Fetching summary..."):
        graph = st.session_state.graph
        summary = graph.execute()
        if not summary:
            summary = "I'm sorry, I couldn't generate a summary for this document."
        st.session_state.summary_result = summary

        st.text_area(
            "<h1>S u m m a r y  R e s u l t</h1>",
            value=st.session_state.summary_result,
            height=500,
            key="summary_result",
            disabled=True,
        )


def handle_keypoints_submit():
    """Handle the submission for extracting key points."""
    with st.spinner("Fetching key points..."):
        graph = st.session_state.graph
        key_points = graph.execute()
        if not key_points:
            key_points = "I'm sorry, I couldn't extract key points from this document."
        st.session_state.key_points_result = key_points

        st.text_area(
            "<h1>K e y  P o i n t s  R e s u l t</h1>",
            value=st.session_state.key_points_result,
            height=500,
            key="key_points_result",
            disabled=True,
        )


def trigger_refresh() -> None:
    """Triggers a refresh by setting the flag."""
    st.session_state.refresh_triggered = True
    st.rerun()


def initialize_session_state() -> None:
    """Initialize session state variables if not already set."""
    session_defaults = {
        "url": "",
        "model_company_key": "OpenAI",
        "model_name_key": "gpt-4o-mini",
        "chatbot_api_key": "",
        "source_key": "URL",
        "task_key": "Chat",
        "temperature_key": 0.7,
        "max_tokens_key": 1000,
        "status": [],
        "graph": None,
        "chat_history": [],
        "scraping_done": False,
        "question_input": "",
        "summary_result": "",
        "key_points_result": "",
        "refresh_triggered": False,
        "selected_task_index": 0,
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
    st.session_state.question_input = ""
    st.session_state.chat_history = []
    st.session_state.model_company_key = "OpenAI"
    st.session_state.model_name_key = "gpt-4o-mini"
    st.session_state.chatbot_api_key = ""
    st.session_state.source_key = "URL"
    st.session_state.task_key = "Chat"
    st.session_state.temperature_key = 0.7
    st.session_state.max_tokens_key = 1000
    st.session_state.selected_task_index = 0
    st.session_state.key_points_result = ""
    st.session_state.summary_result = ""
    st.session_state.scraping_done = False
    st.session_state.qa = (None,)
    st.cache_data.clear()
    st.session_state.refresh_triggered = False
    st.session_state.error_mes = ""
    st.rerun()


if __name__ == "__main__":
    if st.session_state.get("refresh_triggered"):
        clear_state()
    main()
