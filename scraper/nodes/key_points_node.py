"""
Key points node module
"""

import logging
from typing import List, Optional

from langchain import hub
from langchain.chains.combine_documents.reduce import ReduceDocumentsChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.llm import LLMChain
from langchain.chains.mapreduce import MapReduceDocumentsChain
from langchain.prompts import PromptTemplate
from langchain_core.documents import Document
from langchain_text_splitters import CharacterTextSplitter
from scrapegraphai.nodes import BaseNode

from scraper.utils import get_map_prompt_template, get_reduce_prompt_template


class KeyPoints(BaseNode):
    """
    A node responsible for compressing the input tokens and storing the document
    in a vector database for retrieval. Relevant chunks are stored in the state.

    It allows scraping of big documents without exceeding the token limit of the language model.

    Attributes:
        llm_model: An instance of a language model client, configured for generating answers.
        verbose (bool): A flag indicating whether to show print statements during execution.

    Args:
        input (str): Boolean expression defining the input keys needed from the state.
        output (List[str]): List of output keys to be updated in the state.
        node_config (dict): Additional configuration for the node.
        node_name (str): The unique identifier name for the node, defaulting to "Parse".
    """

    def __init__(
        self,
        input: str,
        output: List[str],
        node_config: Optional[dict] = None,
        node_name: str = "keypoints",
    ):
        super().__init__(node_name, "node", input, output, 1, node_config)

        self.llm_model = node_config["llm_model"]
        self.verbose = (
            False if node_config is None else node_config.get("verbose", False)
        )

    def execute(self, state: dict) -> dict:
        """
        Executes the node's logic to implement RAG (Retrieval-Augmented Generation).
        The method updates the state with relevant chunks of the document.

        Args:
            state (dict): The current state of the graph. The input keys will be used to fetch the
                            correct data from the state.

        Returns:
            dict: The updated state with the output key containing the relevant chunks of the document.

        Raises:
            KeyError: If the input keys are not found in the state, indicating that the
                        necessary information for compressing the content is missing.
        """

        logging.info(f"Executing {self.node_name} Node")

        # Interpret input keys based on the provided input expression
        input_keys = self.get_input_keys(state)

        # Fetching data from the state based on the input keys
        input_data = [state[key] for key in input_keys]

        doc = input_data[0]
        chunked_docs = []
        for i, chunk in enumerate(doc):
            doc = Document(
                page_content=chunk,
                metadata={
                    "chunk": i + 1,
                },
            )
            chunked_docs.append(doc)
        logging.info("Updated chunks metadata")

        # Create a prompt template from the map template
        map_prompt = PromptTemplate.from_template(get_map_prompt_template())
        # Create a map chain using the LLM and map prompt
        map_chain = LLMChain(llm=self.llm_model, prompt=map_prompt)

        # Create a prompt template from the reduce template
        reduce_prompt = PromptTemplate.from_template(get_reduce_prompt_template())
        # Create a reduce chain using the LLM and map prompt
        reduce_chain = LLMChain(llm=self.llm_model, prompt=reduce_prompt)

        # Create a StuffDocumentsChain to combine documents into a single string
        combine_documents_chain = StuffDocumentsChain(
            llm_chain=reduce_chain, document_variable_name="docs"
        )

        # Create a ReduceDocumentsChain to iteratively reduce the mapped documents
        reduce_documents_chain = ReduceDocumentsChain(
            combine_documents_chain=combine_documents_chain,
            collapse_documents_chain=combine_documents_chain,
            token_max=10000,
        )

        # Create a MapReduceDocumentsChain to map and reduce documents
        map_reduce_chain = MapReduceDocumentsChain(
            llm_chain=map_chain,
            reduce_documents_chain=reduce_documents_chain,
            document_variable_name="docs",
            return_intermediate_steps=False,
        )

        # Initialize a text splitter to split documents into smaller chunks
        text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=1000, chunk_overlap=0
        )
        # Split the document chunks
        split_docs = text_splitter.split_documents(chunked_docs)
        # Generate the summary by invoking the MapReduce chain with split documents
        summary_result = map_reduce_chain.invoke(split_docs)
        summary_text = summary_result.get("output_text", "")
        logging.info("Successfully generated MapReduce summary.")

        state.update({self.output[0]: summary_text})
        return state
