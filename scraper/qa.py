"""
Module for handling question-answering functionality using LlamaIndex and a vector store for retrieval.
"""

import logging
from typing import List

from llama_index.core import Document, ListIndex, VectorStoreIndex
from llama_index.core.query_engine.router_query_engine import RouterQueryEngine
from llama_index.core.selectors.llm_selectors import LLMSingleSelector
from llama_index.core.tools.query_engine import QueryEngineTool
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai import OpenAI

from scraper.errors import CreateIndexError, QueryError


class QuestionAnswering:
    """
    Handles the question-answering functionality using LlamaIndex and a vector store for retrieval.
    """

    def __init__(
        self,
        documents: List[str],
        embedding_model_name: str,
        open_ai_key: str,
        model_name: str = "gpt-3.5-turbo",
        embedding_model=None,
        llm_model=None,
    ):
        """
        Initializes the QuestionAnswering instance with a list of documents.

        Args:
            documents (List[str]): A list of documents as strings.
            embedding_model_name: Embedding model name.
            open_ai_key: Open AI key for generation.
            model: LLM model.
        """
        self.documents = [Document(text=text) for text in documents]
        self.embed_model = embedding_model or HuggingFaceEmbedding(
            model_name=embedding_model_name
        )
        self.open_ai_key = open_ai_key
        self.conversation_history = []
        self.llm = llm_model or OpenAI(model=model_name, api_key=self.open_ai_key)

    def create_index(self):
        """
        Creates the index from the documents.
        """
        try:
            # Attempt to create a vector index from the nodes
            logging.info("Creating vector index...")
            vector_index = VectorStoreIndex.from_documents(
                documents=self.documents, embed_model=self.embed_model
            )
            if vector_index is None:
                logging.error("Vector index creation failed.")
                return

            # Other initializations
            logging.info("Creating list index...")
            list_index = ListIndex(self.documents)

            logging.info("Setting up list query engines...")
            list_query_engine = list_index.as_query_engine(
                response_mode="tree_summarize", use_async=True, llm=self.llm
            )

            logging.info("Setting up vector tool...")
            vector_tool = QueryEngineTool.from_defaults(
                query_engine=vector_index.as_chat_engine(llm=self.llm),
                description="Retrieves specific content from documents.",
            )

            logging.info("Setting up list tool...")
            list_tool = QueryEngineTool.from_defaults(
                query_engine=list_query_engine,
                description="Summarizes the content from documents.",
            )

            # Combining tools into a router query engine
            logging.info("Combining tools into router query engine...")
            self.query_engine = RouterQueryEngine(
                selector=LLMSingleSelector.from_defaults(llm=self.llm),
                query_engine_tools=[list_tool, vector_tool],
                llm=self.llm,
            )

            logging.info("Index created successfully.")
        except CreateIndexError as e:
            logging.error(f"Failed to create index: {e}")
            raise

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
            # Add the question to the conversation history
            self.conversation_history.append(("Q", question))

            # Formulate the context by concatenating the conversation history
            context = "\n".join(
                [f"{q_or_a}: {text}" for q_or_a, text in self.conversation_history]
            )

            # Query the engine with the given question and context
            logging.info("Query the engine with the given question and context...")
            response = self.query_engine.query(context)
            context = str(response)

            # Query the remote LLM with the context and question
            logging.info("Query the remote LLM with the context and question...")
            llm_response = self.llm.complete(context)

            # Add the response to the conversation history
            logging.info("Add the response to the conversation history...")
            self.conversation_history.append(("A", llm_response))

            return llm_response

        except QueryError as e:
            logging.error(f"Failed to process query: {e}")
            return f"Error: {e}"
