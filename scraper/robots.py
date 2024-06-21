"""
Module to handle fetching and parsing robots.txt for web scraping permissions.
"""

import logging
from typing import Dict, List, Optional
from urllib.parse import urlparse

import requests

from scraper.errors import RobotsTxtError
from scraper.logging import safe_run


class RobotsTxtChecker:
    """
    Fetches and parses the robots.txt file for a given website to manage scraping permissions.
    """

    def __init__(self, base_url: str, requester: Optional[requests.Session] = None):
        """
        Initializes the RobotsTxtChecker with the base URL and an optional requester session.

        Args:
            base_url (str): The base URL of the website.
            requester (Optional[requests.Session]): An optional requests session for making HTTP requests.
        """
        self.requester = requester or requests.Session()
        self.rules: Dict[str, List[str]] = {}
        self.robots_url = self._create_robots_url(base_url)

    def _create_robots_url(self, base_url: str) -> str:
        """
        Creates the URL for the robots.txt file based on the base URL.

        Args:
            base_url (str): The base URL of the website.

        Returns:
            str: The URL for the robots.txt file.
        """
        parsed_url = urlparse(base_url)
        scheme = parsed_url.scheme
        netloc = parsed_url.netloc
        return f"{scheme}://{netloc}/robots.txt"

    def fetch(self) -> None:
        """
        Fetches and parses the robots.txt file.
        """
        try:
            response = self.requester.get(self.robots_url)
            response.raise_for_status()
            self._parse(response.text)
            logging.info("robots.txt fetched and parsed successfully.")
        except requests.RequestException as e:
            if e.response is not None and e.response.status_code == 404:
                logging.warning(
                    f"robots.txt not found at {self.robots_url}, proceeding without it."
                )
            else:
                logging.error(f"Failed to fetch robots.txt from {self.robots_url}: {e}")
                raise RobotsTxtError(f"Error fetching robots.txt: {e}")
        finally:
            self.requester.close()

    @safe_run
    def is_allowed(self, path: str, user_agent: str = "*") -> bool:
        """
        Checks if the path is allowed by robots.txt for the given user agent.

        Args:
            path (str): The path to check.
            user_agent (str): The user agent string (default is "*").

        Returns:
            bool: True if the path is allowed, False otherwise.
        """
        disallow_paths = self.rules.get(user_agent, [])
        for disallow_path in disallow_paths:
            if path.startswith(disallow_path):
                logging.info(
                    f"Access to {path} disallowed for {user_agent} by robots.txt."
                )
                return False
        return True

    def _parse(self, content: str) -> None:
        """
        Parses the robots.txt content.

        Args:
            content (str): The content of the robots.txt file.
        """
        current_user_agent = None
        for line in content.splitlines():
            line = line.strip()
            if line.startswith("User-agent:"):
                current_user_agent = line.split(":")[1].strip()
                self.rules[current_user_agent] = []
            elif line.startswith("Disallow:") and current_user_agent is not None:
                disallow_path = line.split(":")[1].strip()
                self.rules[current_user_agent].append(disallow_path)
        logging.info("robots.txt rules parsed and stored.")
