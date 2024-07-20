"""
Application main logic
"""

import logging
from pathlib import Path
from typing import List

from scraper.errors import PageScrapingError
from scraper.graphs import QAGraph
from scraper.graphs.base_graph import GraphInterface
from scraper.graphs.graph_factory import GraphFactory
from scraper.models import configure_llm, create_models
from scraper.utils import (
    check_robots,
    get_scraper,
    install_playwright_chromium,
    is_valid_url,
    url_exists,
)


def validate_input(session_state) -> bool:
    """Validate user inputs and set error message if invalid."""
    source = session_state.get("source")
    selected_source = session_state.get("selected_source")
    openai_api_key = session_state.get("chatbot_api_key")

    if not source:
        set_error(
            "Source selection cannot be empty. Please enter a valid source.",
            session_state,
        )
        return False

    if selected_source.is_url:
        if not is_valid_url(source):
            set_error("Invalid URL format.", session_state)
            return False
        if not url_exists(source):
            set_error("The URL does not exist.", session_state)
            return False
        if not check_robots(source):
            set_error(
                "The robots.txt file does not allow parsing the URL.", session_state
            )
            return False
    elif not openai_api_key:
        set_error("Please add your OpenAI API key to continue.", session_state)
        return False

    return True


def execute_scraping(session_state: dict) -> None:
    """Executes all processes after performing necessary validations."""
    if not validate_input(session_state):
        return

    try:
        setup_dependencies()
        documents = scrape(session_state)
        llm_config = configure_llm(session_state)
        model_config = create_models(
            session_state["model_company"], llm_config.model_dump()
        )
        graph = GraphFactory.create_graph(
            task_id=session_state.selected_task_index,
            documents=documents,
            llm=model_config.llm,
            embed_model=model_config.embedder,
            content_source=session_state.selected_source.content_source,
        )
        process_and_update_state(graph, session_state)
    except Exception as e:
        handle_error(e, session_state)


def setup_dependencies():
    """Ensure all external dependencies are set up."""
    install_playwright_chromium()


def scrape(session_state: dict) -> List[str]:
    """Scrapes the given URL or PDF and processes the documents for question answering."""
    logging.info(f"Scraping: {session_state.get('source')}")

    selected_source = session_state.get("selected_source")
    source = session_state.get("source")

    if not selected_source.is_url:
        uploaded_file = source
        source = str(save_uploaded_file(uploaded_file))
        logging.info(f"File saved at: {source}")

    # Use factory to get the appropriate scraper
    scraper = get_scraper(selected_source.id, source)

    documents = scraper.scrape()
    if not documents:
        logging.error("Scraper returned None for documents")
        raise PageScrapingError("Failed to scrape documents")

    return documents


def process_and_update_state(graph: GraphInterface, session_state: dict) -> None:
    """Update the session state with results from the scraping."""
    session_state.update(
        {
            "graph": graph,
            "scraping_done": True,
            "error_mes": "",
        }
    )


def save_uploaded_file(uploaded_file, save_dir="/tmp"):
    """
    Saves an uploaded file to the specified directory and returns the path.
    Works across Unix, macOS, and Windows.

    Args:
    uploaded_file: The uploaded file object from Streamlit.
    save_dir: The directory to save the file. Defaults to '/tmp'.

    Returns:
    The path of the saved file as a pathlib.Path object.
    """
    save_directory = Path(save_dir)
    save_directory.mkdir(parents=True, exist_ok=True)
    file_path = save_directory / uploaded_file.name

    # Write the file
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getvalue())

    return file_path


def handle_error(exception: Exception, session_state: dict):
    """Handle exceptions and update session state with error message."""
    error_message = f"An error occurred: {exception}"
    logging.error(error_message, exc_info=True)
    set_error(error_message, session_state)


def set_error(message: str, session_state: dict) -> None:
    """Helper function to set the session state error message."""
    session_state["error_mes"] = message
