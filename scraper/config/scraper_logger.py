# scraper_logger.py
import logging

import streamlit as st


class StreamlitHandler(logging.Handler):
    def __init__(self, log_container):
        super().__init__()
        self.log_container = log_container

    def emit(self, record):
        log_entry = self.format(record)
        with self.log_container:
            st.write(log_entry)
