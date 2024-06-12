# test_qa.py
import logging

from sentence_transformers import SentenceTransformer

from scraper.config.config import MilvusConfig, QAConfig
from scraper.rag.qa import QuestionAnswering
from scraper.rag.vector_db import VectorDatabase


def main():
    # Setup logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # Milvus and QA configuration
    milvus_config = MilvusConfig(
        host="localhost",
        port="19530",
        embedding_model_name="sentence-transformers/all-MiniLM-L6-v2",
    )
    qa_config = QAConfig(
        top_n_chunks=5, embedding_model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # Initialize VectorDatabase instance
    vector_db_instance = VectorDatabase(
        url="https://quotes.toscrape.com/",  # URL is used to generate collection name
        config=milvus_config,
        embedding_model=SentenceTransformer(milvus_config.embedding_model_name),
    )
    vector_db_instance.connect_to_milvus()

    # Access existing collection and documents
    collection_name = vector_db_instance.get_collection_name()
    vector_db_instance.create_or_load_collection(collection_name)
    vector_store = vector_db_instance.get_vector_store()

    # Retrieve existing documents
    query = vector_store.query(expr="id >= 0", output_fields=["document", "metadata"])
    documents = [
        {"text": item["document"], "metadata": item["metadata"]} for item in query
    ]

    if not documents:
        logging.error("No documents found in the vector store.")
        return

    logging.info(f"Retrieved {len(documents)} documents from the vector store.")

    # Initialize QA instance
    qa_instance = QuestionAnswering(
        vector_store=vector_store,
        documents=documents,
        qa_config=qa_config,
        embedding_model=SentenceTransformer(qa_config.embedding_model_name),
    )

    # Test the answer_question method
    test_question = "When did Albert Einstein born?"
    logging.info(f"Testing question: {test_question}")
    answer = qa_instance.answer_question(test_question)
    logging.info(f"Answer: {answer}")


if __name__ == "__main__":
    main()
