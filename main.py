"""
Main application
"""

import streamlit as st

from scraper.logging import setup_logging
from scraper.main import clear_state, initialize_session_state
from scraper.ui_components import ConfigurationUI, QAInterface, ScrapingUI


def main():
    """Main function to set up the Streamlit interface and session state."""
    st.set_page_config(layout="wide")
    st.title("🕸️ Scrape Smart 🧠")

    # Inject custom CSS
    inject_custom_css()

    # Initialize session state variables
    initialize_session_state()

    left_column, _, right_column = st.columns([1, 0.1, 2.6])

    with left_column:
        ScrapingUI.display()
        ConfigurationUI.display()

    with right_column:
        QAInterface.display()

    setup_logging()


def inject_custom_css():
    """Inject custom CSS to style the Streamlit app."""
    st.markdown(
        """
        <style>
            /* Global settings */
            body {
                font-family: 'Helvetica Neue', Arial, sans-serif;
                color: #000000;
            }

            /* Apply to all headers */
            h1 {
                font-size: 2.5em;
                color: #333333;
                font-family: 'Helvetica Neue', Arial, sans-serif;
            }
            h2 {
                font-size: 2.0em;
                color: #333333;
                font-family: 'Helvetica Neue', Arial, sans-serif;
            }
            h3, h4, h5, h6 {
                color: #333333;
                font-family: 'Helvetica Neue', Arial, sans-serif;
            }

            /* Specific widget styles */
            .stTextInput, .stButton, .stSelectbox, .stTextArea, .stSlider {
                font-size: 16px;
                font-family: 'Helvetica Neue', Arial, sans-serif;
                color: #333333;
            }

            /* Container styles */
            .stContainer {
                background-color: #FFFFFF;
            }

            /* Customize chat messages */
            .chat-message-user {
                font-family: 'Helvetica Neue', Arial, sans-serif;
                color: #333333;
                font-size: 16px;
                border-left: 3px solid #4CAF50;
                padding-left: 10px;
                margin-bottom: 10px;
            }

            .chat-message-assistant {
                font-family: 'Helvetica Neue', Arial, sans-serif;
                color: #333333;
                font-size: 16px;
                border-left: 3px solid #007BFF;
                padding-left: 10px;
                margin-bottom: 10px;
            }
        </style>
    """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    if st.session_state.get("refresh_triggered"):
        clear_state()
    main()
