from langgraph.graph import StateGraph, START, END
from typeguard import typechecked
import logging

from src.talking_agents.graph.generate_topics.nodes import GenerateTopicsNodes
from src.talking_agents.graph.generate_topics import GenerateTopicsState
from src.talking_agents.graph import INode

log = logging.getLogger(__name__)


class GenerateTopicsGraph(INode[GenerateTopicsState]):
    @typechecked()
    def __init__(
            self,
            create_topics_node: INode[GenerateTopicsState],
            review_topics_node: INode[GenerateTopicsState],
    ):
        graph_builder = StateGraph(GenerateTopicsState)
        graph_builder.add_node(GenerateTopicsNodes.CREATE_TOPICS, create_topics_node.run)
        graph_builder.add_node(GenerateTopicsNodes.REVIEW_TOPICS, review_topics_node.run)

        graph_builder.add_edge(START, GenerateTopicsNodes.CREATE_TOPICS)
        graph_builder.add_edge(GenerateTopicsNodes.CREATE_TOPICS, GenerateTopicsNodes.REVIEW_TOPICS)
        graph_builder.add_edge(GenerateTopicsNodes.REVIEW_TOPICS, END)

        self._graph = graph_builder.compile()

    @typechecked()
    async def run(self, state: GenerateTopicsState) -> GenerateTopicsState:
        log.info("Start generate topics agent graph.")
        result = GenerateTopicsState.model_validate(await self._graph.ainvoke(state))
        return result
