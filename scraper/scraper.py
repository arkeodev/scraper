"""
Module for web scraping operations.
"""

import logging
import time
from typing import Callable, List, Optional
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

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
        driver: Optional[webdriver.Chrome] = None,
        parser: Optional[Callable] = None,
    ):
        """
        Initializes the WebScraper with the base URL and optional components.

        Args:
            base_url (str): The base URL to scrape.
            robots_checker (Optional[RobotsTxtChecker]): Optional robots.txt checker.
            driver (Optional[webdriver.Chrome]): Optional Selenium WebDriver.
            parser (Optional[Callable]): Optional HTML parser.
        """
        self.base_url = base_url
        self.robots_checker = robots_checker or RobotsTxtChecker(base_url)
        self.driver = driver or self._setup_driver()
        self.parser = parser or BeautifulSoup
        self.documents = []  # Use list to store documents
        self.visited_urls = set()

    def _setup_driver(self) -> webdriver.Chrome:
        """
        Sets up the Chrome WebDriver.

        Returns:
            webdriver.Chrome: Configured Chrome WebDriver.
        """
        options = Options()
        options.headless = True
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--headless")  # Ensure headless mode is set
        logging.info("Setting up Chrome WebDriver")
        return webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()), options=options
        )

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
            self._scrape_page(self.base_url)
        except Exception as e:
            logging.error(f"An error occurred during scraping: {e}")
        finally:
            if self.driver:
                self.driver.quit()  # Ensure the driver is quit after scraping
        logging.info(f"Total documents collected: {len(self.documents)}")
        return self.documents

    def _scrape_page(self, url: str) -> None:
        logging.info(f"Scraping page: {url}")
        self.driver.set_page_load_timeout(ScraperConfig.page_load_timeout)
        self.driver.get(url)
        time.sleep(ScraperConfig.page_load_sleep)
        page_source = self.driver.page_source
        readable_text = extract_readable_text(page_source)
        if readable_text:
            self.documents.append(readable_text)
        else:
            logging.warning(f"No readable text found at {url}")
