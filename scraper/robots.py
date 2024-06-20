"""
Module to handle fetching and parsing robots.txt for web scraping permissions.
"""

import logging
from typing import Dict, List, Optional
from urllib.parse import urlparse

import requests

from scraper.logging import safe_run

import streamlit as st


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
        self.requester = (
            requester or requests.Session()
        )  # Use the provided requester or create a new requests session.
        self.rules: Dict[
            str, List[str]
        ] = {}  # Initialize an empty dictionary to store robots.txt rules.
        self.robots_url = self._create_robots_url(
            base_url
        )  # Construct the URL for the robots.txt file.

    def _create_robots_url(self, base_url: str) -> str:
        """
        Creates the URL for the robots.txt file based on the base URL.

        Returns:
            str: The URL for the robots.txt file.
        """
        netloc = urlparse(
            base_url
        ).netloc  # Parse the base URL to extract the network location.
        return (
            f"http://{netloc}/robots.txt"  # Construct the URL for the robots.txt file.
        )

    @safe_run
    def fetch(self) -> None:
        """
        Fetches and parses the robots.txt file.
        """
        try:
            response = self.requester.get(
                self.robots_url
            )  # Send a GET request to fetch the robots.txt file.
            st.write(f"response status: {response.status_code}")
            response.raise_for_status()
            st.write(f"here1")
            self._parse(response.text)  # Parse the content of the robots.txt file.
            logging.info("robots.txt fetched and parsed successfully.")
        except requests.RequestException as e:
            st.write(f"here2")
            if e.response.status_code == 404:
                st.write(f"here3")
                logging.warning(
                    f"robots.txt not found at {self.robots_url}, proceeding without it."
                )
            else:
                logging.error(f"Failed to fetch robots.txt from {self.robots_url}: {e}")
                raise ConnectionError(f"Error fetching robots.txt: {e}")
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
                return False  # Access is disallowed if the path matches any disallowed paths.
        return True  # Allow access if no disallowed paths match.

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
                current_user_agent = line.split(":")[
                    1
                ].strip()  # Extract the user agent from the line.
                self.rules[
                    current_user_agent
                ] = []  # Initialize a list for disallowed paths.
            elif line.startswith("Disallow:") and current_user_agent is not None:
                disallow_path = line.split(":")[
                    1
                ].strip()  # Extract the disallowed path from the line.
                self.rules[current_user_agent].append(
                    disallow_path
                )  # Add the disallowed path to the rules.
        logging.info("robots.txt rules parsed and stored.")
