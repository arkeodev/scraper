"""
Logging configuration for the application.
"""

import logging
import traceback


def setup_logging():
    """
    Sets up logging configuration for the application.

    Configures the logging to display the timestamp, log level, and message.
    Sets the logging level for specific external packages to WARNING or higher.
    """
    logging.basicConfig(
        level=logging.INFO,  # Set the default logging level to INFO.
        format="%(asctime)s - %(levelname)s - %(message)s",  # Define the log message format.
    )
    # Set logging level for external packages to WARNING or higher to reduce verbosity.
    for package in ["selenium", "urllib3", "requests", "webdriver_manager", "bs4"]:
        logging.getLogger(package).setLevel(logging.WARNING)


def safe_run(func):
    """
    Decorator for safe execution of functions, with logging of exceptions.

    This decorator wraps a function to catch and log any exceptions that occur during its execution,
    along with the stack trace. It helps in preventing the application from crashing due to unhandled exceptions.

    Args:
        func (function): The function to be decorated.

    Returns:
        function: The wrapped function with exception handling.
    """

    def wrapper(*args, **kwargs):
        try:
            return func(
                *args, **kwargs
            )  # Execute the decorated function with its arguments.
        except Exception as e:
            func_name = (
                func.__name__
            )  # Get the name of the function where the exception occurred.
            tb = traceback.format_exc()  # Format the stack trace.
            logging.error(
                f"An error occurred in function '{func_name}': {e}"
            )  # Log the error message.
            logging.error(f"Traceback: {tb}")  # Log the stack trace.
            return None  # Return None in case of an exception.

    return wrapper
