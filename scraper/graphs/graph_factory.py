from typing import List

from scraper.graphs.base_graph import GraphInterface
from scraper.graphs.key_points_graph import KeyPointsGraph
from scraper.graphs.qa_graph import QAGraph
from scraper.graphs.summary_graph import SummarizerGraph


class GraphFactory:
    @staticmethod
    def create_graph(
        task_id: int,
        documents: List[str],
        llm,
        embed_model=None,
        content_source: str = None,
    ) -> GraphInterface:
        if task_id == 1:
            return QAGraph(documents, llm, embed_model, content_source)
        elif task_id == 2:
            return KeyPointsGraph(documents, llm, content_source)
        elif task_id == 3:
            return SummarizerGraph(documents, llm, content_source)
        else:
            raise ValueError("Unknown task ID")
