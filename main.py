import streamlit as st
from dotenv import load_dotenv

from scraper.logging import setup_logging
from ui.components import ConfigurationUI, QAInterface, ScrapingUI


def main():
    """Main function to set up the Streamlit interface and session state."""
    st.set_page_config(layout="wide")
    st.title("🕸️ Scrape Smart 🧠")

    # Initialize session state variables
    initialize_session_state()

    left_column, _, right_column = st.columns([1, 0.1, 2.6])

    with left_column:
        ScrapingUI.display()
        ConfigurationUI.display()

    with right_column:
        QAInterface.display()

    setup_logging()


def initialize_session_state():
    """Initialize session state variables if not already set."""
    session_defaults = {
        "url": "",
        "status": [],
        "qa": None,
        "documents": [],
        "chat_history": [],
        "scraping_done": False,  # Track if scraping is done
        "question_input": "",
        "refresh_triggered": False,  # Flag to trigger refresh
        "error_mes": "",  # Error message state
    }
    for key, value in session_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def clear_state():
    """Clears the session state."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state.status = []
    st.session_state.url_input = ""
    st.session_state.question_input = None
    st.session_state.chat_history = []
    st.session_state.language_key = "english"
    st.session_state.scraping_done = False
    st.cache_data.clear()
    st.session_state.refresh_triggered = False  # Reset the refresh trigger flag
    st.session_state.error_mes = ""  # Reset error message
    st.rerun()


if __name__ == "__main__":
    if st.session_state.get("refresh_triggered"):
        clear_state()
    main()
