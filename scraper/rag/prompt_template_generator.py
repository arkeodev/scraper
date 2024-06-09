def generate_prompt(question: str, context: str) -> str:
    return f"Given the context: {context}\nAnswer the question: {question}"
