"""
Ebook Scraper module
"""

import logging
from typing import List

from scrapegraphai.graphs import BaseGraph
from scrapegraphai.nodes import ParseNode

from scraper.nodes import EbookNode
from scraper.scrapers.scraper import Scraper


class EbookScraper(Scraper):
    def __init__(self, source: str) -> None:
        super().__init__(source)
        self._setup_graph()  # Set up the graph during initialization
        self.input_key = "ebook"

    def _setup_graph(self):
        """
        Sets up the graph with the necessary nodes and configurations.
        """
        self.ebook_node = EbookNode(
            input="ebook",
            output=["doc"],
            node_config={
                "verbose": True,
                "headless": True,
            },
        )

        self.parse_node = ParseNode(
            input="doc",
            output=["parsed_doc"],
            node_config={"parse_html": False, "chunk_size": 4096},
        )

        self.graph = BaseGraph(
            nodes=[self.ebook_node, self.parse_node],
            edges=[(self.ebook_node, self.parse_node)],
            entry_point=self.ebook_node,
        )

    def scrape(self) -> List[str]:
        """
        Executes the graph to fetch and parse the document from a given PDF document.

        Returns:
            A list of parsed document segments or an empty list if an error occurs or if no data is parsed.
        """
        try:
            # Execute the graph
            result, _ = self.graph.execute(
                {"user_prompt": "", self.input_key: self.source}
            )
            # Get the parsed document from the result
            doc_list = result.get("doc", [])
            if doc_list:
                logging.info(f"Total {len(doc_list)} documents.")
            else:
                logging.warning("No parsed document found.")
            return doc_list
        except Exception as e:
            logging.error(f"Error during scraping: {e}", exc_info=True)
            return []
