"""
PDF Scraper module
"""

import logging
from typing import List

from scrapegraphai.graphs import BaseGraph
from scrapegraphai.nodes import FetchNode, ParseNode

from scraper.interfaces import Scraper


class PdfScraper(Scraper):
    def __init__(self, source: str) -> None:
        super().__init__(source)
        self._setup_graph()  # Set up the graph during initialization
        self.input_key = "pdf" if source.endswith("pdf") else "pdf_dir"

    def _setup_graph(self):
        """
        Sets up the graph with the necessary nodes and configurations.
        """
        self.fetch_node = FetchNode(
            input="pdf | pdf_dir",
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
            nodes=[self.fetch_node, self.parse_node],
            edges=[(self.fetch_node, self.parse_node)],
            entry_point=self.fetch_node,
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
                {"user_prompt": "Describe the content", "pdf": self.source}
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
