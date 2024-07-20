"""
Answer generation node module
"""

import logging
from typing import List, Optional

from langchain.output_parsers import OutputFixingParser
from langchain.prompts import PromptTemplate
from langchain.schema import OutputParserException
from langchain_core.documents import Document
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableParallel
from scrapegraphai.nodes import BaseNode
from tqdm import tqdm

from scraper.config import AnswerSchema
from scraper.content_detector import ContentFormatGuesser
from scraper.utils import get_merging_prompt_template, get_unified_prompt_template


class GenerateAnswerNode(BaseNode):
    def __init__(
        self,
        input: str,
        output: List[str],
        node_config: Optional[dict] = None,
        node_name: str = "generateanswer",
    ):
        super().__init__(node_name, "node", input, output, 2, node_config)
        self.llm_model = node_config.get("llm_model")
        self.verbose = node_config.get("verbose", False)
        self.output_schema = node_config.get("schema", AnswerSchema)
        self.content_source = node_config.get("content_source", "url")

    def execute(self, state: dict) -> dict:
        logging.info(f"Executing {self.node_name} Node")
        input_keys = self.get_input_keys(state)
        input_data = [state[key] for key in input_keys]
        user_prompt = input_data[0]
        doc: List[Document] = input_data[1]

        output_parser = JsonOutputParser(pydantic_object=self.output_schema)
        format_instructions = output_parser.get_format_instructions()

        single_chunk = True if len(doc) == 1 else False
        cfg = ContentFormatGuesser()
        content_format = cfg.guess_format(doc[0].page_content)
        prompt_template = get_unified_prompt_template(
            self.content_source, content_format, single_chunk
        )

        try:
            if len(doc) == 1:
                # Handling single chunk of content
                prompt = PromptTemplate(
                    template=prompt_template,
                    input_variables=[
                        "question",
                        "format_instructions",
                        "context",
                    ],
                    partial_variables={
                        "context": doc[0].page_content,
                        "question": user_prompt,
                        "format_instructions": format_instructions,
                    },
                )
                answer = (prompt | self.llm_model | output_parser).invoke(
                    {"question": user_prompt}
                )
            else:
                # Handling multiple chunks
                chains_dict = {}
                for i, chunk in enumerate(
                    tqdm(doc, desc="Processing chunks", disable=not self.verbose)
                ):
                    prompt = PromptTemplate(
                        template=prompt_template,
                        input_variables=[
                            "question",
                            "format_instructions",
                            "context",
                        ],
                        partial_variables={
                            "context": chunk.page_content,
                            "question": user_prompt,
                            "format_instructions": format_instructions,
                        },
                    )
                    chain_name = f"chunk{i+1}"
                    chains_dict[chain_name] = prompt | self.llm_model | output_parser
                # Collect results
                parallel_results = RunnableParallel(**chains_dict).invoke(
                    {"question": user_prompt}
                )
                # Merge results with another LLM prompt
                merge_prompt = PromptTemplate(
                    template=get_merging_prompt_template(self.content_source),
                    input_variables=["context", "question"],
                    partial_variables={"format_instructions": format_instructions},
                )
                answer = (merge_prompt | self.llm_model | output_parser).invoke(
                    {"context": parallel_results, "question": user_prompt}
                )
        except OutputParserException:
            fixing_parser = OutputFixingParser.from_llm(
                parser=output_parser, llm=self.llm_model
            )
            answer = fixing_parser.parse(answer)

        state.update({self.output[0]: answer})
        return state
