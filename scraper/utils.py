"""
Utility functions for text extraction, URL validation, and prompt template generation.
"""

import logging
import os
import subprocess
import sys

import requests
import trafilatura
from readability import Document

from subprocess import CalledProcessError

from scraper.errors import BrowserLaunchError


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
    Extracts readable text from HTML content using readability-lxml and trafilatura.

    Args:
        html (str): The HTML content to extract readable text from.

    Returns:
        str: The extracted readable text, or an empty string if extraction fails.
    """
    try:
        doc = Document(html)  # Parse the HTML content using readability-lxml.
        readable_html = doc.summary()  # Get the readable HTML content.
        readable_text = trafilatura.extract(
            readable_html
        )  # Extract readable text using trafilatura.
        return (
            readable_text.strip() if readable_text else ""
        )  # Return the extracted text, stripped of leading/trailing whitespace.
    except Exception as e:
        logging.error(f"Error extracting text: {e}")
        return ""  # Return an empty string if extraction fails.


def extract_text_trafilatura(html: str) -> str:
    """
    Extracts readable text from HTML content using trafilatura directly.

    Args:
        html (str): The HTML content to extract readable text from.

    Returns:
        str: The extracted readable text, or an empty string if extraction fails.
    """
    try:
        readable_text = trafilatura.extract(
            html
        )  # Extract readable text using trafilatura.
        return (
            readable_text.strip() if readable_text else ""
        )  # Return the extracted text, stripped of leading/trailing whitespace.
    except Exception as e:
        logging.error(f"Error extracting text with trafilatura: {e}")
        return ""  # Return an empty string if extraction fails.


def is_valid_url(url: str) -> bool:
    """
    Validates the URL format.

    Args:
        url (str): The URL to validate.

    Returns:
        bool: True if the URL is valid, False otherwise.
    """
    from urllib.parse import urlparse

    parsed = urlparse(url)  # Parse the URL.
    return bool(parsed.scheme) and bool(
        parsed.netloc
    )  # Check if the URL has a scheme and network location.


def url_exists(url: str) -> bool:
    """
    Checks if the URL exists by sending a HEAD request.

    Args:
        url (str): The URL to check.

    Returns:
        bool: True if the URL exists, False otherwise.
    """
    try:
        response = requests.head(
            url, allow_redirects=True, timeout=5
        )  # Send a HEAD request to the URL.
        return (
            response.status_code == 200
        )  # Return True if the response status code is 200 (OK).
    except requests.RequestException as e:
        logging.error(f"URL check failed: {e}")
        return False  # Return False if the request fails.


def install_playwright_chromium() -> None:
    """
    Installs Playwright and the necessary Chromium browser.
    """
    try:
        import playwright

        logging.info("Playwright is already installed.")
    except ImportError:
        logging.info("Installing Playwright...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright"])
        logging.info("Playwright installed successfully.")

    try:
        subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"], check=True
        )
        logging.info("Playwright Chromium browser installed successfully.")

        subprocess.run(
            ["sudo", sys.executable, "-m", "playwright", "install-deps"], check=True
        )
        logging.info("Playwright Chromium browser dependencies installed successfully.")
    except CalledProcessError as e:
        logging.error(
            f"Failed to install Playwright Chromium and its dependencies: {e}"
        )
        raise BrowserLaunchError("Failed to install Playwright Chromium browser")
