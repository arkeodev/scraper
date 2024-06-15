"""
Module for handling question-answering functionality using LlamaIndex and a vector store for retrieval.
"""

import logging
from typing import List

from llama_index.core import Document, ListIndex, ServiceContext, VectorStoreIndex
from llama_index.core.query_engine.router_query_engine import RouterQueryEngine
from llama_index.core.selectors.llm_selectors import LLMSingleSelector
from llama_index.core.tools.query_engine import QueryEngineTool


class QuestionAnswering:
    """
    Handles the question-answering functionality using LlamaIndex and a vector store for retrieval.
    """

    def __init__(self, documents: List[str]):
        logging.info(f"Number of documents received: {len(documents)}")
        self.documents = [Document(text=text) for text in documents]
        self.query_engine = None

    def create_index(self):
        """
        Creates the index from the documents.
        """
        service_context = ServiceContext.from_defaults(chunk_size=1024)
        nodes = (
            service_context.node_parser.get_nodes_from_documents(self.documents)
            if len(self.documents) > 1
            else self.documents
        )
        vector_index = VectorStoreIndex.from_documents(nodes)
        list_index = ListIndex(nodes)

        list_query_engine = list_index.as_query_engine(
            response_mode="tree_summarize", use_async=True
        )

        vector_tool = QueryEngineTool.from_defaults(
            query_engine=vector_index.as_chat_engine(),
            description="Retrieves specific content from documents.",
        )

        list_tool = QueryEngineTool.from_defaults(
            query_engine=list_query_engine,
            description="Summarizes the content from documents.",
        )

        self.query_engine = RouterQueryEngine(
            selector=LLMSingleSelector.from_defaults(),
            query_engine_tools=[list_tool, vector_tool],
        )

    def query(self, question: str) -> str:
        """
        Queries the index and retrieves an answer based on the input question.

        Args:
            question (str): The question to ask.

        Returns:
            str: The answer to the question.
        """
        if not self.query_engine:
            logging.error("Query engine has not been created. Load documents first.")
            return "Query engine has not been created. Load documents first."

        try:
            response = self.query_engine.query(question)
            return str(response)
        except Exception as e:
            logging.error(f"Failed to process query: {e}")
            return f"Error: {e}"
