"""
Module: prompt_template.py
Purpose: Provides the prompt template for generating responses in the QA system.
"""


def get_prompt_template() -> str:
    """
    Returns the prompt template for generating QA responses.

    Returns:
        str: The prompt template.
    """
    return (
        "You are an AI assistant. Given the following context, answer the question to the best of your ability.\n"
        "Context: {context}\n"
        "Question: {question}\n"
        "Answer:"
    )
