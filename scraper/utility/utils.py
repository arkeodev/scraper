"""
Utility functions for text extraction and prompt template generation.
"""

import logging

import requests
import trafilatura
from readability import Document


def get_prompt_template() -> str:
    """
    Returns the prompt template for generating QA responses.

    Returns:
        str: The prompt template.
    """
    return (
        "You are an AI assistant. Given the following context, answer the question to the best of your ability.\n"
        "Context: {context}\n"
        "Question: {question}\n"
        "Answer:"
    )


def extract_readable_text(html: str) -> str:
    """
    Extracts readable text from HTML content using readability-lxml.

    Args:
        html (str): The HTML content to extract readable text from.

    Returns:
        str: The extracted readable text.
    """
    try:
        doc = Document(html)
        readable_html = doc.summary()
        readable_text = trafilatura.extract(readable_html)
        return readable_text.strip()
    except Exception as e:
        logging.error(f"Error extracting text: {e}")
        return ""


def extract_text_trafilatura(html: str) -> str:
    """
    Extracts readable text from HTML content using trafilatura directly.

    Args:
        html (str): The HTML content to extract readable text from.

    Returns:
        str: The extracted readable text.
    """
    try:
        readable_text = trafilatura.extract(html)
        return readable_text.strip() if readable_text else ""
    except Exception as e:
        logging.error(f"Error extracting text with trafilatura: {e}")
        return ""


def is_valid_url(url: str) -> bool:
    """
    Validates the URL format.

    Args:
        url (str): The URL to validate.

    Returns:
        bool: True if the URL is valid, False otherwise.
    """
    from urllib.parse import urlparse

    parsed = urlparse(url)
    return bool(parsed.scheme) and bool(parsed.netloc)


def url_exists(url: str) -> bool:
    """
    Checks if the URL exists by sending a HEAD request.

    Args:
        url (str): The URL to check.

    Returns:
        bool: True if the URL exists, False otherwise.
    """
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False
