import logging
import subprocess
import sys
import time
from typing import Callable, List, Optional
from urllib.parse import urlparse

import streamlit as st
from bs4 import BeautifulSoup
from playwright.sync_api import Browser
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Playwright, sync_playwright

from scraper.config import ScraperConfig
from scraper.robots import RobotsTxtChecker
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
        """
        Initializes the WebScraper with the base URL and optional components.

        Args:
            base_url (str): The base URL to scrape.
            robots_checker (Optional[RobotsTxtChecker]): Optional robots.txt checker.
            parser (Optional[Callable]): Optional HTML parser.
        """
        self.base_url = base_url
        self.robots_checker = robots_checker or RobotsTxtChecker(base_url)
        self.parser = parser or BeautifulSoup
        self.documents = []  # Use list to store documents
        self.visited_urls = set()
        self._install_playwright_chromium()

    def _install_playwright_chromium(self) -> None:
        """
        Installs Playwright and the necessary browsers.
        """
        try:
            import playwright  # Check if playwright is already installed

            logging.info("Playwright is already installed.")
        except ImportError:
            logging.info("Installing Playwright...")
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "playwright"]
            )
            logging.info("Playwright installed successfully.")

        logging.info("Installing Playwright Chromium browser...")
        try:
            subprocess.run(
                [sys.executable, "-m", "playwright", "install", "chromium"], check=True
            )
            logging.info("Playwright Chromium browser installed successfully.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to install Playwright Chromium browser: {e}")
            raise

    def _setup_browser(self, playwright: Playwright) -> Browser:
        """
        Sets up the Playwright Browser.

        Returns:
            Browser: Configured Playwright Browser.
        """
        logging.info("Setting up Playwright Chromium Browser")
        try:
            return playwright.chromium.launch(headless=True)
        except PlaywrightError as e:
            logging.error(f"An error occurred while launching the browser: {e}")
            raise

    def scrape(self) -> List[str]:
        """
        Starts the scraping process.

        Returns:
            List[str]: List of scraped documents.
        """
        try:
            logging.info("Starting scraping process")
            self.robots_checker.fetch()  # Fetch and parse robots.txt
            if not self.robots_checker.is_allowed(urlparse(self.base_url).path):
                logging.info(f"Access to {self.base_url} disallowed by robots.txt.")
                return []

            with sync_playwright() as playwright:
                try:
                    browser = self._setup_browser(playwright)
                    self._scrape_page(browser, self.base_url)
                    browser.close()
                except PlaywrightError as e:
                    logging.error(f"An error occurred during scraping: {e}")
        except Exception as e:
            logging.error(f"An error occurred during scraping: {e}")
        logging.info(f"Total documents collected: {len(self.documents)}")
        return self.documents

    def _scrape_page(self, browser: Browser, url: str) -> None:
        logging.info(f"Scraping page: {url}")
        page = browser.new_page()
        page.goto(url)
        time.sleep(ScraperConfig.page_load_sleep)
        page_source = page.content()
        readable_text = extract_readable_text(page_source)
        if readable_text:
            self.documents.append(readable_text)
        else:
            logging.warning(f"No readable text found at {url}")
        page.close()
