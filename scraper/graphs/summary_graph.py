"""
Graph module handling refined summarizer functionality.
"""

import logging
from typing import List, Optional

from scrapegraphai.graphs import BaseGraph

from scraper.errors import SummarizerError
from scraper.graphs.base_graph import GraphInterface
from scraper.nodes.summarizer_node import Summarizer


class SummarizerGraph(GraphInterface):
    """
    Handles refinement sumary.
    """

    def __init__(self, documents: List[str], llm, content_source: str):
        """
        Initializes the SummarizerGraph instance with a list of documents and model configurations.

        Args:
            documents: A list of documents as strings.
            llm: llm model.
        """
        self.documents = documents
        self.llm = llm
        self.content_source = content_source
        self._setup_graph()

    def _setup_graph(self):
        """
        Sets up the graph with the necessary nodes and configurations.
        """
        summary_node = Summarizer(
            input="parsed_doc | doc",
            output=["summary"],
            node_config={
                "llm_model": self.llm,
                "verbose": True,
                "content_source": self.content_source,
            },
        )
        self.graph = BaseGraph(
            nodes=[summary_node],
            edges=[],
            entry_point=summary_node,
            use_burr=False,
            burr_config={
                "project_name": "universal-scraper",
                "app_instance_id": "001",
            },
        )

    def execute(self) -> Optional[str]:
        """
        Executes the graph to generate an answer for a given prompt.

        Returns:
            The summary string, or None if no answer is found.
        """
        logging.info("Summarizing document")
        try:
            result, execution_info = self.graph.execute({"doc": self.documents})
            logging.info(f"Execution info: {execution_info}")

            # Extract summary from the result dictionary
            summary = result.get("summary", None)
            logging.info(f"Summary results: {summary}")

            if summary:
                return summary
            else:
                logging.info("No summary generated by the model.")
                return None

        except SummarizerError as e:
            logging.error(f"Summarizing failed: {e}")
            return None