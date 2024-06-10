import logging
import threading
import time
from typing import Callable, List, Optional, Set
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from scraper.config.config import AppConfig, ScraperConfig
from scraper.config.logging import safe_run
from scraper.scraping.robots import RobotsTxtChecker


class WebScraper:
    """
    A class responsible for web scraping operations.
    """

    def __init__(
        self,
        base_url: str,
        update_progress: Callable[[str], None],
        robots_checker: Optional[RobotsTxtChecker] = None,
        driver: Optional[webdriver.Chrome] = None,
        parser: Optional[Callable] = None,
    ):
        """
        Initializes the WebScraper with necessary parameters.

        Args:
            base_url (str): The base URL of the website to scrape.
            update_progress (Callable[[str], None]): Callback function to update progress.
            robots_checker (Optional[RobotsTxtChecker]): Instance of RobotsTxtChecker, defaults to a new instance if not provided.
            driver (Optional[webdriver.Chrome]): Instance of Chrome WebDriver, defaults to a new instance if not provided.
            parser (Optional[Callable]): HTML parser, defaults to BeautifulSoup if not provided.
        """
        self.base_url = base_url
        self.update_progress = update_progress
        self.robots_checker = (
            robots_checker if robots_checker else RobotsTxtChecker(base_url)
        )
        self.driver = driver if driver else self._setup_driver()
        self.parser = parser if parser else BeautifulSoup
        self.lock = threading.Lock()
        self.last_request_time = 0
        self.visited_urls: Set[str] = set()
        self.documents: List[str] = []
        self.max_links = ScraperConfig().max_links
        self.page_load_sleep = ScraperConfig().page_load_sleep
        self.page_load_timeout = ScraperConfig().page_load_timeout

    def _setup_driver(self) -> webdriver.Chrome:
        """
        Sets up the Chrome WebDriver.

        Returns:
            webdriver.Chrome: Configured Chrome WebDriver instance.
        """
        options = Options()
        options.headless = True
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        logging.info("Setting up Chrome WebDriver")
        return webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()), options=options
        )

    def wait_for_next_request(self) -> None:
        """
        Ensures the minimum interval between requests is maintained.
        """
        with self.lock:
            current_time = time.time()
            time_since_last_request = current_time - self.last_request_time
            if time_since_last_request < AppConfig().min_interval_between_requests:
                wait_time = (
                    AppConfig().min_interval_between_requests - time_since_last_request
                )
                time.sleep(wait_time)
            self.last_request_time = time.time()

    def is_same_domain(self, url: str) -> bool:
        """
        Checks if a URL belongs to the same domain as the base URL.

        Args:
            url (str): The URL to check.

        Returns:
            bool: True if the URL belongs to the same domain, False otherwise.
        """
        return urlparse(url).netloc == urlparse(self.base_url).netloc

    @safe_run
    def scrape(self) -> List[str]:
        """
        Initiates the scraping process.

        Returns:
            List[str]: List of extracted text content.
        """
        try:
            self.robots_checker.fetch()
            self._scrape_recursive(self.base_url)
        except Exception as e:
            logging.error(f"An error occurred during scraping: {e}")
            self.update_progress(f"An error occurred during scraping: {e}")
        finally:
            if self.driver:
                self.driver.quit()
        return self.documents

    @safe_run
    def _scrape_recursive(self, url: str) -> None:
        """
        Recursively scrapes the website starting from the given URL.

        Args:
            url (str): The URL to start scraping from.
        """
        if url in self.visited_urls or len(self.visited_urls) >= self.max_links:
            return
        self.visited_urls.add(url)

        if not self.robots_checker.is_allowed(urlparse(url).path):
            logging.info(f"Access to {url} disallowed by robots.txt.")
            self.update_progress(f"Access to {url} disallowed by robots.txt.")
            return

        self.wait_for_next_request()

        try:
            self.update_progress(f"Scraping {url}...")
            logging.info(f"Fetching URL: {url}")
            self.driver.set_page_load_timeout(self.page_load_timeout)
            self.driver.get(url)
            time.sleep(self.page_load_sleep)  # Wait for page to fully load
            page_source = self.driver.page_source
            soup = self.parser(page_source, "html.parser")
            texts = [p.get_text(strip=True) for p in soup.find_all("p")]
            self.documents.extend(texts)

            for link in soup.find_all("a", href=True):
                if len(self.visited_urls) >= self.max_links:
                    break
                full_url = urljoin(url, link["href"])
                if self.is_same_domain(full_url):
                    self._scrape_recursive(full_url)
        except TimeoutException:
            logging.error(f"Timeout while trying to load {url}")
            self.update_progress(f"Timeout while trying to load {url}")
        except WebDriverException as e:
            logging.error(f"WebDriver error: {e}")
            self.update_progress(f"WebDriver error: {e}")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            self.update_progress(f"An unexpected error occurred: {e}")
