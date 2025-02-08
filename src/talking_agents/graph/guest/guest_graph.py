from langgraph.graph import StateGraph, START, END
from langchain_core.messages import AIMessage
from typeguard import typechecked
import logging

from src.talking_agents.graph.guest.nodes import Nodes
from src.talking_agents.graph.guest import GuestState
from src.talking_agents.graph import INode

log = logging.getLogger(__name__)


class GuestGraph(INode[GuestState]):
    @typechecked()
    def __init__(
            self,
            casual_question_answering_node: INode[GuestState],
            paper_question_answering_node: INode[GuestState],
    ):
        graph_builder = StateGraph(GuestState)
        graph_builder.add_node(Nodes.CASUAL_QUESTION_ANSWERING, casual_question_answering_node.run)
        graph_builder.add_node(Nodes.PAPER_QUESTION_ANSWERING, paper_question_answering_node.run)

        graph_builder.add_conditional_edges(START, self._chose_question_path)
        # casual question answering path
        graph_builder.add_edge(Nodes.CASUAL_QUESTION_ANSWERING, END)
        # paper question answering path
        graph_builder.add_edge(Nodes.PAPER_QUESTION_ANSWERING, END)

        self._graph = graph_builder.compile()

    @typechecked()
    def _chose_question_path(self, state: GuestState) -> Nodes | str:
        if state.next_question == -1:
            return Nodes.CASUAL_QUESTION_ANSWERING
        elif state.next_question >= len(state.preparation.questions):
            return Nodes.CASUAL_QUESTION_ANSWERING
        return Nodes.PAPER_QUESTION_ANSWERING

    @typechecked()
    async def run(self, state: GuestState) -> GuestState:
        log.info("Start interview guest agent graph.")
        result = GuestState.model_validate(await self._graph.ainvoke(state))
        return result
