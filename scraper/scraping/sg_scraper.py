import logging
from typing import List

from scrapegraphai.graphs import BaseGraph
from scrapegraphai.nodes import FetchNode, ParseNode

from scraper.interfaces import Scraper
from scraper.utils import extract_readable_text


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

            parsed_doc = extract_readable_text(parsed_doc_list[0])
            logging.info(f"Document size: {len(parsed_doc)} characters")
            return list(parsed_doc)

        except Exception as e:
            logging.error(f"Error during scraping: {e}")
            return []


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
            "openai_api_key": model_config.api_key,
            "model_name": model_config.llm_model_name,
        }
        self.llm = OpenAI(llm_config=llm_config)
        self.conversation_history = []

    def rag(self, prompt: str) -> str:
        try:
            # Add the question to the conversation history
            self.conversation_history.append(("Q", prompt))

            # Formulate the context by concatenating the conversation history
            context = "\n".join(
                [f"{q_or_a}: {text}" for q_or_a, text in self.conversation_history]
            )

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

            # Execute the graph
            result, execution_info = graph.execute(
                {"user_prompt": prompt, "parsed_doc": self.documents}
            )

            # get the answer from the result
            result = result.get("answer", "No answer found.")
            print(result)
            print(execution_info)

            # Add the response to the conversation history
            logging.info(f"Add the response to the conversation history: {result}")
            self.conversation_history.append(("A", result))
            return result

        except QueryError as e:
            logging.error(f"Failed to process query: {e}")
            return f"Error: {e}"


def main() -> None:
    url = "https://kirlangicyuvasi.com/2016/11/18/hakikat-saadet-umitsizlik/"
    scraper = SgScraper(url)
    documents = scraper.scrape()
    model_name = "gpt-3.5-turbo"
    embedding_model_name = "emrecan/bert-base-turkish-cased-mean-nli-stsb-tr"
    openai_api_key = "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"
    temperature = 0.7
    max_tokens = 10_000
    llm_config = LLMConfig(
        llm_model_name=model_name,
        embedding_model_name=embedding_model_name,
        api_key=openai_api_key,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    rag = SgRag(documents=documents, model_config=llm_config)
    answer = rag.rag("Bir insanın ömrü nasil ölçülmeli?")
    print(answer)


if __name__ == "__main__":
    main()
