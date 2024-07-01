"""
Application main logic
"""

import logging
from pathlib import Path

from scraper.config import LLMConfig, embedding_models_dict
from scraper.errors import PageScrapingError
from scraper.interfaces import Rag
from scraper.pdf_scraper import PdfScraper
from scraper.qa import SgRag
from scraper.url_scraper import UrlScraper
from scraper.utils import (
    check_robots,
    install_playwright_chromium,
    is_valid_url,
    url_exists,
)


def initiate_scraping_process(session_state):
    """Begins the scraping task after performing necessary validations."""
    if not validate_input(session_state):
        return

    try:
        setup_dependencies()
        llm_config = configure_llm(session_state)
        process_and_update_state(
            scrape_and_process(session_state, llm_config), session_state
        )
    except Exception as e:
        handle_error(e, session_state)


def validate_input(session_state) -> bool:
    """Validate user inputs and set error message if invalid."""
    source = session_state.get("source")
    input_type = session_state.get("input_type")
    openai_api_key = session_state.get("chatbot_api_key")
    if not source:
        set_error(
            "Source selection cannot be empty. Please enter a valid source.",
            session_state,
        )
        return False
    elif input_type == "url":
        if not is_valid_url(source):
            set_error("Invalid URL format.")
            return
        if not url_exists(source):
            set_error("The URL does not exist.")
            return
        if not check_robots(source):
            set_error("The robots.txt file not allow to parse the URL.")
            return
    elif not openai_api_key:
        set_error("Please add your OpenAI API key to continue.")
        return
    return True


def setup_dependencies():
    """Ensure all external dependencies are set up."""
    install_playwright_chromium()


def configure_llm(session_state) -> LLMConfig:
    """Configure and return the LLM configuration settings."""
    return LLMConfig(
        llm_model_name=session_state.get("model_name_key"),
        embedding_model_name=embedding_models_dict.get(
            session_state.get("language_key", "english")
        ),
        api_key=session_state.get("openai_key"),
        temperature=session_state.get("temperature_key"),
        max_tokens=session_state.get("max_tokens_key"),
    )


def scrape_and_process(session_state: dict, llm_config: LLMConfig) -> Rag:
    """Scrapes the given URL or PDF and processes the documents for question answering."""
    logging.info(f"Scraping: {session_state.get('source')}")
    logging.info(f"Using embedding model: {llm_config.embedding_model_name}")
    if session_state.get("input_type") == "url":
        scraper = UrlScraper(source=session_state.get("source"))
    else:
        uploaded_file = session_state.get("source")
        file_path = save_uploaded_file(uploaded_file)
        logging.info(f"File saved at: {file_path}")
        scraper = PdfScraper(source=str(file_path))
    documents = scraper.scrape()
    if not documents:
        logging.error("Scraper returned None for documents")
        raise PageScrapingError("Failed to scrape documents")
    rag_instance = SgRag(documents, llm_config)

    return rag_instance


def process_and_update_state(rag_instance, session_state):
    """Update the session state with results from the scraping."""
    session_state.update(
        {
            "qa": rag_instance,
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
    save_directory.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
    file_path = save_directory / uploaded_file.name

    # Write the file
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getvalue())

    return file_path


def handle_error(exception, session_state):
    """Handle exceptions and update session state with error message."""
    error_message = f"An error occurred: {exception}"
    logging.error(error_message, exc_info=True)
    set_error(error_message, session_state)


def set_error(message: str, session_state) -> None:
    """Helper function to set the session state error message."""
    session_state["error_mes"] = message
