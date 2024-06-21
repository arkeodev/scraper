"""
Module for web scraping operations using Playwright.
"""

import logging
import time
from typing import Callable, List, Optional
from urllib.parse import urlparse

from playwright.sync_api import Browser
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Playwright, sync_playwright

from scraper.config import ScraperConfig
from scraper.errors import BrowserLaunchError
from scraper.robots import RobotsTxtChecker
from scraper.utils import extract_readable_text

import streamlit as st


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
        st.write(f"here1:")
        self.base_url = base_url
        self.robots_checker = robots_checker or RobotsTxtChecker(base_url)
        self.parser = parser or extract_readable_text
        self.documents = []  # Use list to store documents
        st.write(f"here2:")

    def _setup_browser(self, playwright: Playwright) -> Browser:
        """
        Sets up the Playwright Browser.

        Returns:
            Browser: Configured Playwright Browser.
        """
        logging.info("Setting up Playwright Chromium Browser")
        try:
            st.write(f"here3")
            pr = playwright.chromium.launch(headless=True)
            st.write(f"here4: {pr.browser_type}")
            return pr
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
            self.robots_checker.fetch()
            if not self.robots_checker.is_allowed(urlparse(self.base_url).path):
                logging.info(f"Access to {self.base_url} disallowed by robots.txt.")
                return []

            with sync_playwright() as playwright:
                browser = self._setup_browser(playwright)
                self._scrape_page(browser, self.base_url)
                browser.close()
        except Exception as e:
            logging.error(f"An error occurred during scraping: {e}")
        logging.info(f"Total documents collected: {len(self.documents)}")
        return self.documents

    def _scrape_page(self, browser: Browser, url: str) -> None:
        """
        Scrapes a single page.

        Args:
            browser (Browser): The Playwright browser instance.
            url (str): The URL of the page to scrape.
        """
        logging.info(f"Scraping page: {url}")
        page = browser.new_page()
        page.goto(url)
        time.sleep(ScraperConfig.page_load_sleep)
        page_source = page.content()
        readable_text = self.parser(page_source)
        if readable_text:
            self.documents.append(readable_text)
        else:
            logging.warning(f"No readable text found at {url}")
        page.close()
