# scraper.py
import logging
import time
from typing import Callable, List, Optional, Set
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from dask import compute, delayed
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
        config: ScraperConfig,
        robots_checker: Optional[RobotsTxtChecker] = None,
        driver: Optional[webdriver.Chrome] = None,
        parser: Optional[Callable] = None,
    ):
        self.base_url = base_url
        self.robots_checker = (
            robots_checker if robots_checker else RobotsTxtChecker(base_url)
        )
        self.driver = driver if driver else self._setup_driver()
        self.parser = parser if parser else BeautifulSoup
        self.config = config if config else ScraperConfig()
        self.max_links = self.config.max_links
        self.page_load_sleep = self.config.page_load_sleep
        self.page_load_timeout = self.config.page_load_timeout
        self.visited_urls: Set[str] = set()
        self.documents: List[str] = []

    def _setup_driver(self) -> webdriver.Chrome:
        options = Options()
        options.headless = True
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        logging.info("Setting up Chrome WebDriver")
        return webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()), options=options
        )

    @safe_run
    def scrape(self) -> List[str]:
        try:
            self.robots_checker.fetch()
            links_to_scrape = self._get_links(self.base_url)
            delayed_tasks = [
                delayed(self.scrape_page)(link) for link in links_to_scrape
            ]
            results = compute(*delayed_tasks, scheduler="threads")
            self.documents.extend([doc for sublist in results for doc in sublist])
        except Exception as e:
            logging.error(f"An error occurred during scraping: {e}")
        finally:
            if self.driver:
                self.driver.quit()
        return self.documents

    @safe_run
    def scrape_page(self, url: str) -> List[str]:
        if url in self.visited_urls or len(self.visited_urls) >= self.max_links:
            return []
        self.visited_urls.add(url)
        if not self.robots_checker.is_allowed(urlparse(url).path):
            logging.info(f"Access to {url} disallowed by robots.txt.")
            return []
        time.sleep(
            AppConfig().min_interval_between_requests
        )  # Ensure minimum interval between requests
        documents = []
        try:
            logging.info(f"Fetching URL: {url}")
            self.driver.set_page_load_timeout(self.page_load_timeout)
            self.driver.get(url)
            time.sleep(self.page_load_sleep)
            page_source = self.driver.page_source
            soup = self.parser(page_source, "html.parser")
            texts = [p.get_text(strip=True) for p in soup.find_all("p")]
            documents.extend(texts)
        except TimeoutException:
            logging.error(f"Timeout while trying to load {url}")
        except WebDriverException as e:
            logging.error(f"WebDriver error: {e}")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
        return documents

    def _get_links(self, url: str) -> List[str]:
        try:
            self.driver.set_page_load_timeout(self.page_load_timeout)
            self.driver.get(url)
            time.sleep(self.page_load_sleep)
            soup = self.parser(self.driver.page_source, "html.parser")
            links = [
                urljoin(url, link["href"]) for link in soup.find_all("a", href=True)
            ]
            same_domain_links = [link for link in links if self.is_same_domain(link)]
            return same_domain_links[: self.max_links]
        except Exception as e:
            logging.error(f"Error while getting links from {url}: {e}")
            return []

    def is_same_domain(self, url: str) -> bool:
        return urlparse(url).netloc == urlparse(self.base_url).netloc
