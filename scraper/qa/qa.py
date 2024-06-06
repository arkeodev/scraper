# scraping/qa/qa.py
import numpy as np
import torch
from transformers import AutoModel, AutoModelForQuestionAnswering, AutoTokenizer


class QuestionAnswering:
    def __init__(
        self,
        vector_store,
        embedding_model_name="sentence-transformers/all-MiniLM-L6-v2",
        qa_model_name="distilbert-base-uncased-distilled-squad",
    ):
        self.vector_store = vector_store
        self.embedding_model_name = embedding_model_name
        self.qa_model_name = qa_model_name
        (
            self.embedding_model,
            self.embedding_tokenizer,
        ) = self._initialize_embedding_model()
        self.qa_model, self.qa_tokenizer = self._initialize_qa_model()

    def _initialize_embedding_model(self):
        tokenizer = AutoTokenizer.from_pretrained(self.embedding_model_name)
        model = AutoModel.from_pretrained(self.embedding_model_name)
        return model, tokenizer

    def _initialize_qa_model(self):
        tokenizer = AutoTokenizer.from_pretrained(self.qa_model_name)
        model = AutoModelForQuestionAnswering.from_pretrained(self.qa_model_name)
        return model, tokenizer

    def embed_text(self, text):
        inputs = self.embedding_tokenizer(
            text, return_tensors="pt", padding=True, truncation=True
        )
        with torch.no_grad():
            outputs = self.embedding_model(**inputs)
        embeddings = outputs.last_hidden_state.mean(dim=1)
        return embeddings.numpy()

    def answer_question(self, question, documents):
        question_embedding = self.embed_text(question)
        D, I = self.vector_store.search(question_embedding, k=1)
        nearest_doc_index = I[0][0]
        context = documents[nearest_doc_index]["text"]

        inputs = self.qa_tokenizer(question, context, return_tensors="pt")
        with torch.no_grad():
            outputs = self.qa_model(**inputs)

        answer_start = torch.argmax(outputs.start_logits)
        answer_end = torch.argmax(outputs.end_logits) + 1
        answer = self.qa_tokenizer.convert_tokens_to_string(
            self.qa_tokenizer.convert_ids_to_tokens(
                inputs["input_ids"][0][answer_start:answer_end]
            )
        )

        return answer
