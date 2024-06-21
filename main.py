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

    # Set up three columns, using st.columns
    left_column, _, right_column = st.columns([1, 0.1, 2.6])

    with left_column:
        ScrapingUI.display()
        ConfigurationUI.display()
        # Add a space and then the GitHub link at the bottom
        st.write("")  # This adds a bit of space
        # Add styled GitHub link at the bottom
        st.markdown(
            "<a class='github-link' href='https://github.com/arkeodev/scraper' target='_blank'>"
            "<span class='github-icon'></span>View on GitHub</a>",
            unsafe_allow_html=True,
        )

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

            /* Link styles */
            .github-link {
                font-family: 'Helvetica Neue', Arial, sans-serif;
                font-size: 16px;
                color: #333333;
                text-decoration: none;
                border: none;
                background-color: transparent;
                cursor: pointer;
                display: flex;
                align-items: center;
                padding: 10px 0;
            }

            .github-link:hover {
                text-decoration: underline;
            }

            .github-icon {
                display: inline-block;
                background-image: url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iOTgiIGhlaWdodD0iOTYiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHBhdGggZmlsbC1ydWxlPSJldmVub2RkIiBjbGlwLXJ1bGU9ImV2ZW5vZGQiIGQ9Ik00OC44NTQgMEMyMS44MzkgMCAwIDIyIDAgNDkuMjE3YzAgMjEuNzU2IDEzLjk5MyA0MC4xNzIgMzMuNDA1IDQ2LjY5IDIuNDI3LjQ5IDMuMzE2LTEuMDU5IDMuMzE2LTIuMzYyIDAtMS4xNDEtLjA4LTUuMDUyLS4wOC05LjEyNy0xMy41OSAyLjkzNC0xNi40Mi01Ljg2Ny0xNi40Mi01Ljg2Ny0yLjE4NC01LjcwNC01LjQyLTcuMTctNS40Mi03LjE3LTQuNDQ4LTMuMDE1LjMyNC0zLjAxNS4zMjQtMy4wMTUgNC45MzQuMzI2IDcuNTIzIDUuMDUyIDcuNTIzIDUuMDUyIDQuMzY3IDcuNDk2IDExLjQwNCA1LjM3OCAxNC4yMzUgNC4wNzQuNDA0LTMuMTc4IDEuNjk5LTUuMzc4IDMuMDc0LTYuNi0xMC44MzktMS4xNDEtMjIuMjQzLTUuMzc4LTIyLjI0My0yNC4yODMgMC01LjM3OCAxLjk0LTkuNzc4IDUuMDE0LTEzLjItLjQ4NS0xLjIyMi0yLjE4NC02LjI3NS40ODYtMTMuMDM4IDAgMCA0LjEyNS0xLjMwNCAxMy40MjYgNS4wNTJhNDYuOTcgNDYuOTcgMCAwIDEgMTIuMjE0LTEuNjNjNC4xMjUgMCA4LjMzLjU3MSAxMi4yMTMgMS42MyA5LjMwMi02LjM1NiAxMy40MjctNS4wNTIgMTMuNDI3LTUuMDUyIDIuNjcgNi43NjMuOTcgMTEuODE2LjQ4NSAxMy4wMzggMy4xNTUgMy40MjIgNS4wMTUgNy44MjIgNS4wMTUgMTMuMiAwIDE4LjkwNS0xMS40MDQgMjMuMDYtMjIuMzI0IDI0LjI4MyAxLjc4IDEuNTQ4IDMuMzE2IDQuNDgxIDMuMzE2IDkuMTI2IDAgNi42LS4wOCAxMS44OTctLjA4IDEzLjUyNiAwIDEuMzA0Ljg5IDIuODUzIDMuMzE2IDIuMzY0IDE5LjQxMi02LjUyIDMzLjQwNS0yNC45MzUgMzMuNDA1LTQ2LjY5MUM5Ny43MDcgMjIgNzUuNzg4IDAgNDguODU0IDB6IiBmaWxsPSIjMjQyOTJmIi8+PC9zdmc+');
                background-size: contain;
                width: 20px;
                height: 20px;
                margin-right: 5px;
            }
        </style>
    """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    if st.session_state.get("refresh_triggered"):
        clear_state()
    main()
