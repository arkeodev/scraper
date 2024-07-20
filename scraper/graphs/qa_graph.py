"""
Graph module handling question-answering functionality.
"""

import logging
from typing import List, Optional

from scrapegraphai.graphs import BaseGraph

from scraper.errors import QueryError
from scraper.graphs.base_graph import GraphInterface
from scraper.nodes.generate_answer_node import GenerateAnswerNode
from scraper.nodes.qa_node import QuestionAnswer


class QAGraph(GraphInterface):
    """
    Handles the Retrieval-Augmented Generation (RAG) functionality for question answering.
    """

    def __init__(self, documents: List[str], llm, embed_model, content_source: str):
        """
        Initializes the QuestionAnswering instance with a list of documents and model configurations.

        Args:
            documents: A list of documents as strings.
            llm: llm model.
            embed_model: embedding model.
        """
        self.documents = documents
        self.embed_model = embed_model
        self.llm = llm
        self.content_source = content_source
        self._setup_graph()

    def _setup_graph(self):
        """
        Sets up the graph with the necessary nodes and configurations.
        """
        self.rag_node = QuestionAnswer(
            input="user_prompt & (parsed_doc | doc)",
            output=["relevant_chunks"],
            node_config={
                "llm_model": self.llm,
                "embedder_model": self.embed_model,
                "verbose": True,
                "content_source": self.content_source,
            },
        )
        self.generate_answer_node = GenerateAnswerNode(
            input="user_prompt & (relevant_chunks | parsed_doc | doc)",
            output=["answer"],
            node_config={"llm_model": self.llm, "verbose": True},
        )
        self.graph = BaseGraph(
            nodes=[self.rag_node, self.generate_answer_node],
            edges=[(self.rag_node, self.generate_answer_node)],
            entry_point=self.rag_node,
            use_burr=False,
            burr_config={
                "project_name": "universal-scraper",
                "app_instance_id": "001",
            },
        )

    def execute(self, prompt: str) -> Optional[str]:
        """
        Executes the graph to generate an answer for a given prompt.

        Args:
            prompt: The user's query or question as a string.

        Returns:
            The generated answer as a string, or None if no answer is found.
        """
        logging.info(f"Received question: {prompt}")
        try:
            result, execution_info = self.graph.execute(
                {"user_prompt": prompt, "doc": self.documents}
            )
            logging.info(f"Execution info: {execution_info}")

            # Extract answers from the result dictionary
            returnings: dict = result.get("answer", {})
            logging.info(f"Answers extracted: {returnings}")

            if returnings and len(returnings["answers"]) > 0:
                most_relevant_answer = max(
                    returnings.get("answers"),
                    key=lambda x: x.get("relevance", 0),
                    default=None,
                )
                relevance = most_relevant_answer.get("relevance", 0)
                source = returnings.get("source", "Unknown")
                logging.info(f"Most relevant answer: {most_relevant_answer['text']}")
                logging.info(f"Relevance: {relevance}")
                logging.info(f"Source: {source}")
                return f"{most_relevant_answer['text']}"
            else:
                logging.info("No answers generated by the model.")
                return None

        except QueryError as e:
            logging.error(f"Query processing failed: {e}")
            return None
