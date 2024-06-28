import logging
from typing import List

from scrapegraphai.graphs import BaseGraph
from scrapegraphai.nodes import FetchNode, ParseNode

from scraper.interfaces import Scraper


class SgScraper(Scraper):
    def __init__(self, url: str) -> None:
        super().__init__(url)

    def scrape(self) -> List[str]:
        fetch_node = FetchNode(
            input="url | local_dir",
            output=["doc", "link_urls", "img_urls"],
            node_config={
                "verbose": True,
                "headless": True,
            },
        )

        parse_node = ParseNode(
            input="doc",
            output=["parsed_doc"],
            node_config={
                "chunk_size": 4096,
                "verbose": True,
            },
        )

        graph = BaseGraph(
            nodes=[fetch_node, parse_node],
            edges=[(fetch_node, parse_node)],
            entry_point=fetch_node,
        )

        try:
            # Execute the graph
            result, _ = graph.execute(
                {"user_prompt": "Describe the content", "url": self.url}
            )

            # Get the parsed document from the result
            parsed_doc_list = result.get("parsed_doc", [])
            if not parsed_doc_list:
                logging.warning("No parsed document found.")
                return []

            logging.info(f"Document size: {len(parsed_doc_list)} characters")
            return parsed_doc_list

        except Exception as e:
            logging.error(f"Error during scraping: {e}")
            return []
