"""
Logging configuration for the application.
"""

import logging
import traceback


def setup_logging():
    """
    Sets up logging configuration.
    """
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    # Set logging level for external packages to WARNING or higher
    for package in ["selenium", "urllib3", "requests", "webdriver_manager", "bs4"]:
        logging.getLogger(package).setLevel(logging.WARNING)


def safe_run(func):
    """
    Decorator for safe execution of functions, with logging of exceptions.

    Args:
        func: The function to be decorated.

    Returns:
        The wrapped function.
    """

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
