"""
Module for web scraping operations using Playwright.
"""

import logging
import time
from typing import List
from urllib.parse import urlparse

from playwright.sync_api import Browser
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright

from scraper.config import ScraperConfig
from scraper.errors import BrowserLaunchError, PageScrapingError
from scraper.interfaces import Scraper
from scraper.utils import extract_readable_text


class WebScraper(Scraper):
    """
    A class responsible for web scraping operations.
    """

    def __init__(self, url: str):
        self.url = url
        self.documents = []  # Use list to store documents

    def _setup_browser(self) -> Browser:
        """
        Sets up the Playwright Browser.

        Returns:
            Browser: Configured Playwright Browser.
        """
        logging.info("Launching Playwright Chromium Browser")
        try:
            playwright = sync_playwright().start()
            return playwright.chromium.launch(headless=True)
        except PlaywrightError as e:
            logging.error(f"An error occurred while launching the browser: {e}")
            raise BrowserLaunchError("Failed to launch the Playwright browser")

    def scrape(self) -> List[str]:
        """
        Starts the scraping process.

        Returns:
            List[str]: List of scraped documents.
        """
        try:
            logging.info("Starting scraping process")
            browser = self._setup_browser()
            logging.info(f"Scraping page: {self.url}")
            page = browser.new_page()
            page.goto(self.url)
            time.sleep(ScraperConfig().page_load_sleep)
            page_source = page.content()
            self._parse_page(page_source)
            page.close()
            browser.close()
        except PageScrapingError as e:
            logging.error(f"An error occurred during scraping: {e}")
        logging.info(f"Total documents collected: {len(self.documents)}")
        return self.documents

    def _parse_page(self, page_content: str) -> None:
        """
        Scrapes a single page.

        Args:
            page_content (str): The content of the page to scrape.
        """
        readable_text = extract_readable_text(page_content)
        if readable_text:
            self.documents.append(readable_text)
            return
        logging.warning(f"No readable text found at {self.url}")
