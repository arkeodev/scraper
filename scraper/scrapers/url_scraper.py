"""
URL Scraper module
"""

import logging
from typing import List

from scrapegraphai.graphs import BaseGraph
from scrapegraphai.nodes import FetchNode, ParseNode

from scraper.interface import Scraper


class UrlScraper(Scraper):
    def __init__(self, source: str) -> None:
        super().__init__(source)
        self._setup_graph()  # Set up the graph during initialization

    def _setup_graph(self):
        """
        Sets up the graph with the necessary nodes and configurations.
        """
        self.fetch_node = FetchNode(
            input="url | local_dir",
            output=["doc", "link_urls", "img_urls"],
            node_config={
                "verbose": True,
                "headless": True,
            },
        )

        self.parse_node = ParseNode(
            input="doc",
            output=["parsed_doc"],
            node_config={
                "chunk_size": 4096,
                "verbose": True,
            },
        )

        self.graph = BaseGraph(
            nodes=[self.fetch_node, self.parse_node],
            edges=[(self.fetch_node, self.parse_node)],
            entry_point=self.fetch_node,
        )

    def scrape(self) -> List[str]:
        """
        Executes the graph to fetch and parse the document from a given URL.

        Returns:
            A list of parsed document segments or an empty list if an error occurs or if no data is parsed.
        """
        try:
            # Execute the graph
            result, _ = self.graph.execute(
                {"user_prompt": "Describe the content", "url": self.source}
            )

            # Get the parsed document from the result
            parsed_doc_list = result.get("parsed_doc", [])
            if parsed_doc_list:
                logging.info(f"Document size: {len(parsed_doc_list)} characters")
            else:
                logging.warning("No parsed document found.")
            return parsed_doc_list

        except Exception as e:
            logging.error(f"Error during scraping: {e}", exc_info=True)
            return []
