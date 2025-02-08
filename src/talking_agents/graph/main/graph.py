from langgraph.graph import StateGraph, START, END
from typeguard import typechecked
import logging

from src.talking_agents.graph.main.state import State
from src.talking_agents.graph.main.nodes import Nodes
from src.talking_agents.graph import INode
from src.talking_agents.graph.common import is_max_state, get_max_state

log = logging.getLogger(__name__)


class Graph(INode[State]):
    @typechecked()
    def __init__(
            self,
            prepare_node: INode[State],
            interview_node: INode[State],
            post_processing_node: INode[State]
    ):
        graph_builder = StateGraph(State)
        graph_builder.add_node(Nodes.PREPARE, prepare_node.run)
        graph_builder.add_node(Nodes.INTERVIEW, interview_node.run)
        graph_builder.add_node(Nodes.POST_PROCESSING, post_processing_node.run)

        graph_builder.add_edge(START, Nodes.PREPARE)
        graph_builder.add_conditional_edges(Nodes.PREPARE, self._goto_interview)
        graph_builder.add_conditional_edges(Nodes.INTERVIEW, self._goto_post_processing)
        graph_builder.add_edge(Nodes.POST_PROCESSING, END)

        self._graph = graph_builder.compile()

    async def run(self, state: State) -> State:
        log.info("Start main agent graph.")
        state.max_state = get_max_state([], state.setup.max_state, 0, Nodes)
        result = State.model_validate(await self._graph.ainvoke(state))
        return result


    @staticmethod
    @typechecked()
    def _goto_interview(state: State) -> Nodes | str:
        if is_max_state(state.max_state, Nodes.PREPARE):
            return END
        return Nodes.INTERVIEW

    @staticmethod
    @typechecked()
    def _goto_post_processing(state: State) -> Nodes | str:
        if is_max_state(state.max_state, Nodes.INTERVIEW):
            return END
        return Nodes.POST_PROCESSING
