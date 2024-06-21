"""
Module for web scraping operations using Playwright.
"""

import logging
import time
from typing import Callable, List, Optional
from urllib.parse import urlparse

from playwright.sync_api import Browser
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright

from scraper.config import ScraperConfig
from scraper.errors import BrowserLaunchError, PageScrapingError
from scraper.robots import RobotsTxtChecker, RobotsTxtError
from scraper.utils import extract_readable_text


class WebScraper:
    """
    A class responsible for web scraping operations.
    """

    def __init__(
        self,
        base_url: str,
        robots_checker: Optional[RobotsTxtChecker] = None,
        parser: Optional[Callable] = None,
    ):
        self.base_url = base_url
        self.robots_checker = robots_checker or RobotsTxtChecker(base_url)
        self.parser = parser or extract_readable_text
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
            if not self._check_robots():
                logging.info(f"Access to {self.base_url} disallowed by robots.txt.")
                return []

            browser = self._setup_browser()
            logging.info(f"Scraping page: {self.base_url}")
            page = browser.new_page()
            page.goto(self.base_url)
            time.sleep(ScraperConfig.page_load_sleep)
            page_source = page.content()
            self._parse_page(page_source)
            page.close()
            browser.close()
        except PageScrapingError as e:
            logging.error(f"An error occurred during scraping: {e}")
        logging.info(f"Total documents collected: {len(self.documents)}")
        return self.documents

    def _check_robots(self) -> bool:
        """
        Checks the robots.txt file for permissions.

        Returns:
            bool: True if allowed to scrape, False otherwise.
        """
        try:
            self.robots_checker.fetch()
            return self.robots_checker.is_allowed(urlparse(self.base_url).path)
        except RobotsTxtError as e:
            logging.error(f"An error occurred while checking robots.txt: {e}")
            return False

    def _parse_page(self, page_content: str) -> None:
        """
        Scrapes a single page.

        Args:
            page_content (str): The content of the page to scrape.
        """
        readable_text = self.parser(page_content)
        if readable_text:
            self.documents.append(readable_text)
            return
        logging.warning(f"No readable text found at {self.base_url}")
