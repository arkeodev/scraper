import logging
import traceback


def setup_logging():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )


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
