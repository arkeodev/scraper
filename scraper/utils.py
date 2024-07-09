"""
Utility functions for text extraction, URL validation, and prompt template generation.
"""

import logging
import os
from urllib.parse import urlparse

import requests
import trafilatura
from readability import Document

from scraper.errors import BrowserLaunchError, RobotsTxtError
from scraper.scrapers import EbookScraper, PdfScraper, UrlScraper
from scraper.scrapers.robots import RobotsTxtChecker
from scraper.scrapers.scraper import Scraper


def get_scraper(task_id: int, source: str) -> Scraper:
    if task_id == 1:  # Parse a URL
        return UrlScraper(source)
    elif task_id == 2:  # Parse PDF file(s)
        return PdfScraper(source)
    elif task_id == 3:  # Parse E-pub file(s)
        return EbookScraper(source)
    else:
        raise ValueError("Invalid task ID")


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
        os.system("playwright install chromium")
        logging.info("Playwright Chromium browser installed successfully.")
        os.system("playwright install-deps")
        logging.info("Playwright Chromium browser dependencies installed successfully.")
    except Exception as e:
        logging.error(
            f"Failed to install Playwright Chromium and its dependencies: {e}"
        )
        raise BrowserLaunchError("Failed to install Playwright Chromium browser")


def check_robots(url) -> bool:
    """
    Checks the robots.txt file for permissions.

    Returns:
        bool: True if allowed to scrape, False otherwise.
    """
    try:
        robots_checker = RobotsTxtChecker(url)
        robots_checker.fetch()
        return robots_checker.is_allowed(urlparse(url).path)
    except RobotsTxtError as e:
        logging.error(f"An error occurred while checking robots.txt: {e}")
        return False
