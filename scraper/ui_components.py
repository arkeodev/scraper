"""
User interface components
"""

import streamlit as st

from scraper.main import start_scraping, trigger_refresh


class ConfigurationUI:
    """Class to handle the display of the sidebar configuration."""

    @staticmethod
    def display() -> None:
        """Display configuration options for the scraper."""
        st.header("Configuration")
        st.session_state.language = st.selectbox(
            "Select the Language of the Web Site:",
            options=("english", "turkish"),
            placeholder="Select language...",
            index=0,
            key="language_key",
            disabled=st.session_state.scraping_done,
        )


class ScrapingUI:
    """Class to handle the display and functionality of the scraping task."""

    @staticmethod
    def display() -> None:
        st.header("AI-Powered Web Scraping")
        url = st.text_input(
            "Enter the URL of the website to scrape:",
            key="url_input",
            disabled=st.session_state.scraping_done,
            placeholder="http://example.com",
        )
        st.session_state.url = url
        running_placeholder = st.empty()
        if st.session_state.error_mes:
            st.error(f"{st.session_state.error_mes}")
        st.button(
            "Start",
            on_click=lambda: start_scraping(running_placeholder),
            disabled=st.session_state.scraping_done,
        )
        st.button("Refresh", on_click=trigger_refresh)


class QAInterface:
    """Class to handle the display and functionality of the QA interface."""

    @staticmethod
    def display() -> None:
        """Displays the QA interface for user interaction."""
        if st.session_state.scraping_done:
            chat_history_container = st.container(height=620, border=False)
            with chat_history_container:
                for role, content in st.session_state.chat_history:
                    st.markdown(
                        f"<div class='chat-message-{role}'>{content}</div>",
                        unsafe_allow_html=True,
                    )

            chat_input_container = st.container(height=80, border=False)
            with chat_input_container:
                chat_input = st.chat_input(
                    "Please ask your questions", key="question_input"
                )

            if st.session_state.qa and chat_input:
                with st.spinner("Fetching answer..."):
                    answer = st.session_state.qa.query(chat_input)
                    st.session_state.chat_history.append(("user", chat_input))
                    st.session_state.chat_history.append(("assistant", answer))
                    st.rerun()  # Re-run to display new messages
