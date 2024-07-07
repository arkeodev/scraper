""""
E-book reader node
"""

from typing import List, Optional

from scrapegraphai.nodes.base_node import BaseNode
from tika import parser


class EbookNode(BaseNode):
    """
    A node responsible for fetching the Ebook content of a e-book document and updating
    the graph's state with this content.

    Attributes:
        headless (bool): A flag indicating whether the browser should run in headless mode.
        verbose (bool): A flag indicating whether to print verbose output during execution.

    Args:
        input (str): Boolean expression defining the input keys needed from the state.
        output (List[str]): List of output keys to be updated in the state.
        node_config (Optional[dict]): Additional configuration for the node.
        node_name (str): The unique identifier name for the node, defaulting to "Fetch".
    """

    def __init__(
        self,
        input: str,
        output: List[str],
        node_config: Optional[dict] = None,
        node_name: str = "ebook",
    ):
        super().__init__(node_name, "node", input, output, 1, node_config)

        self.headless = (
            True if node_config is None else node_config.get("headless", True)
        )
        self.verbose = (
            False if node_config is None else node_config.get("verbose", False)
        )
        self.useSoup = (
            False if node_config is None else node_config.get("useSoup", False)
        )
        self.loader_kwargs = (
            {} if node_config is None else node_config.get("loader_kwargs", {})
        )

    def execute(self, state):
        """
        Executes the node's logic to fetch Ebook content from a e-book document and
        update the state with this content.

        Args:
            state (dict): The current state of the graph. The input keys will be used
                            to fetch the correct data types from the state.

        Returns:
            dict: The updated state with a new output key containing the fetched e-book content.
        """

        self.logger.info(f"--- Executing {self.node_name} Node ---")

        # Interpret input keys based on the provided input expression
        input_keys = self.get_input_keys(state)
        # Fetching data from the state based on the input keys
        input_data = [state[key] for key in input_keys]

        source = input_data[0]
        # Handling ebook
        if input_keys[0] == "ebook":
            parsed = parser.from_file(source)
            compressed_document = parsed["content"]
            state.update({self.output[0]: compressed_document})
            return state
        else:
            raise ValueError("No e-book content found in the document.")
