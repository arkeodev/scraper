# link_collector.py
import logging
import time
from typing import Callable, List
from urllib.parse import urljoin, urlparse, urlunparse

from bs4 import BeautifulSoup
from selenium import webdriver

from scraper.config.config import AppConfig


class LinkCollector:
    """
    Collects all links from a base URL that are in the same domain and below the given URL path.
    """

    def __init__(self, base_url: str, driver: webdriver.Chrome, parser: Callable):
        self.base_url = base_url
        self.base_path = urlparse(base_url).path
        self.driver = driver
        self.parser = parser
        self.visited_urls = set()
        self.last_request_time = 0

    def collect_all_links(
        self, page_load_timeout: int, page_load_sleep: int
    ) -> List[str]:
        """
        Collects all links under the base URL that are in the same domain and below the base URL path.

        Args:
            page_load_timeout (int): The timeout for loading pages.
            page_load_sleep (int): The sleep time after loading a page.

        Returns:
            List[str]: A list of collected links.
        """
        collected_links = []
        links_to_visit = [(self.base_url, 0)]

        while links_to_visit:
            current_url, depth = links_to_visit.pop(0)
            if current_url in self.visited_urls or depth > 3:
                continue

            self.visited_urls.add(current_url)

            new_links = self._get_links(current_url, page_load_timeout, page_load_sleep)
            for link in new_links:
                if link not in self.visited_urls:
                    links_to_visit.append((link, depth + 1))
                    collected_links.append(link)

        return collected_links

    def _get_links(
        self, url: str, page_load_timeout: int, page_load_sleep: int
    ) -> List[str]:
        self._wait_for_next_request()
        try:
            logging.info(f"Getting links from URL: {url}")
            self.driver.set_page_load_timeout(page_load_timeout)
            self.driver.get(url)
            time.sleep(page_load_sleep)
            soup = self.parser(self.driver.page_source, "html.parser")
            links = [
                urljoin(url, link["href"]) for link in soup.find_all("a", href=True)
            ]
            filtered_links = [
                self._normalize_link(link)
                for link in links
                if self._is_same_domain_and_path(link)
            ]
            filtered_links = list(set(filtered_links))  # Remove duplicates
            logging.info(
                f"Found {len(filtered_links)} same domain and path links from {url}"
            )
            return filtered_links
        except Exception as e:
            logging.error(f"Error while getting links from {url}: {e}")
            return []

    def _is_same_domain_and_path(self, url: str) -> bool:
        parsed_url = urlparse(url)
        base_url_parsed = urlparse(self.base_url)
        return (
            parsed_url.netloc == base_url_parsed.netloc
            and parsed_url.path.startswith(self.base_path)
        )

    def _normalize_link(self, url: str) -> str:
        """
        Normalize URL by removing fragment identifiers and optionally query parameters.
        """
        parsed_url = urlparse(url)
        # Remove fragment identifiers
        normalized_url = parsed_url._replace(fragment="")
        # Optionally, remove query parameters
        normalized_url = normalized_url._replace(query="")
        return urlunparse(normalized_url)

    def _wait_for_next_request(self) -> None:
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < AppConfig().min_interval_between_requests:
            wait_time = (
                AppConfig().min_interval_between_requests - time_since_last_request
            )
            logging.info(f"Waiting for {wait_time} seconds before next request")
            time.sleep(wait_time)
        self.last_request_time = time.time()
