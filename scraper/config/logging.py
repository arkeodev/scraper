# logging.py
import asyncio
import logging
import traceback

from scraper.config.scraper_logger import StreamlitHandler


def setup_logging(log_container=None):
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    # Set logging level for external packages to WARNING or higher
    for package in ["selenium", "urllib3", "requests", "webdriver_manager", "bs4"]:
        logging.getLogger(package).setLevel(logging.WARNING)

    if log_container is not None:
        streamlit_handler = StreamlitHandler(log_container)
        streamlit_handler.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        streamlit_handler.setFormatter(formatter)
        logging.getLogger().addHandler(streamlit_handler)


def safe_run(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            func_name = func.__name__
            tb = traceback.format_exc()
            logging.error(f"An error occurred in function '{func_name}': {e}")
            logging.error(f"Traceback: {tb}")
            return None

    return wrapper
