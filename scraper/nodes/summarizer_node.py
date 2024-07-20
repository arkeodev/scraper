"""
Summarizer node module
"""

import logging
from typing import List, Optional

from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document
from scrapegraphai.nodes import BaseNode


class Summarizer(BaseNode):
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
        node_name: str = "summarizer",
    ):
        super().__init__(node_name, "node", input, output, 2, node_config)

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

        summarize_chain = load_summarize_chain(
            llm=self.llm_model, chain_type="refine", verbose=True
        )
        # Generate the summary by invoking the chain with document chunks
        summary = summarize_chain.invoke(chunked_docs)
        logging.info("Successfully generated refine summary.")

        state.update({self.output[0]: summary})
        return state
