"""
Module for handling question-answering functionality using LlamaIndex and a vector store for retrieval.
"""

import logging
from typing import List

from langchain_openai import OpenAIEmbeddings
from scrapegraphai.graphs import BaseGraph
from scrapegraphai.models import OpenAI
from scrapegraphai.nodes import GenerateAnswerNode, RAGNode

from scraper.config import LLMConfig
from scraper.errors import QueryError
from scraper.interfaces import Rag


class SgRag(Rag):
    """
    Handles the RAG functionality.
    """

    def __init__(self, documents: List[str], model_config: LLMConfig):
        """
        Initializes the QuestionAnswering instance with a list of documents.

        Args:
            documents (List[str]): A list of documents as strings.
            model_config: Model parameters
        """
        self.documents = documents
        self.embed_model = OpenAIEmbeddings(api_key=model_config.api_key)
        llm_config = {
            "model_name": model_config.llm_model_name,
            "openai_api_key": model_config.api_key,
            "max_tokens": model_config.max_tokens,
            "temperature": model_config.temperature,
        }
        self.llm = OpenAI(llm_config=llm_config)
        self.conversation_history = []

    def rag(self, prompt: str) -> str:
        try:
            # Add the question to the conversation history
            # self.conversation_history.append(("Q", prompt))
            logging.info(f"The question is: {prompt}")

            # Formulate the context by concatenating the conversation history
            # context = "\n".join(
            #     [f"{q_or_a}: {text}" for q_or_a, text in self.conversation_history]
            # )

            # Define the graph nodes
            rag_node = RAGNode(
                input="user_prompt & (parsed_doc | doc)",
                output=["relevant_chunks"],
                node_config={
                    "llm_model": self.llm,
                    "embedder_model": self.embed_model,
                    "verbose": True,
                },
            )
            generate_answer_node = GenerateAnswerNode(
                input="user_prompt & (relevant_chunks | parsed_doc | doc)",
                output=["answer"],
                node_config={
                    "llm_model": self.llm,
                    "verbose": True,
                },
            )

            # Create the graph by defining the connections
            graph = BaseGraph(
                nodes=[
                    rag_node,
                    generate_answer_node,
                ],
                edges=[(rag_node, generate_answer_node)],
                entry_point=rag_node,
            )

            logging.info(f"Document: {self.documents}")

            # Execute the graph
            result, execution_info = graph.execute(
                {"user_prompt": prompt, "parsed_doc": self.documents}
            )

            logging.info(f"The result is: {result}")

            # get the answer from the result
            result = result.get("answer", "No answer found.")

            # Add the response to the conversation history
            logging.info(f"The response is: {result}")
            # self.conversation_history.append(("A", result))
            return result

        except QueryError as e:
            logging.error(f"Failed to process query: {e}")
            return f"Error: {e}"
