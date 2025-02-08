from langgraph.graph import StateGraph, START, END
from typeguard import typechecked
import logging

from src.talking_agents.graph.interview.nodes import Nodes
from src.talking_agents.graph.interview.interview_state import InterviewState
from src.talking_agents.graph.common.interview_content import InterviewRoles
from src.talking_agents.graph import INode

log = logging.getLogger(__name__)


class InterviewGraph(INode[InterviewState]):
    @typechecked()
    def __init__(
            self,
            moderator_node: INode[InterviewState],
            guest_node: INode[InterviewState],
    ):
        graph_builder = StateGraph(InterviewState)
        graph_builder.add_node(Nodes.MODERATOR, moderator_node.run)
        graph_builder.add_node(Nodes.GUEST, guest_node.run)

        graph_builder.add_conditional_edges(START, self._transition)
        graph_builder.add_conditional_edges(Nodes.MODERATOR, self._transition)
        graph_builder.add_conditional_edges(Nodes.GUEST, self._transition)

        self._graph = graph_builder.compile()

    @typechecked()
    async def run(self, state: InterviewState) -> InterviewState:
        log.info("Start interview agent graph.")
        result = InterviewState.model_validate(await self._graph.ainvoke(
            state,
            {"recursion_limit": 40},
        ))
        return result

    @typechecked()
    def _transition(self, state: InterviewState) -> Nodes | str:
        state.content.store(
            output_path=state.setup.output_path,
            episode_number=state.setup.episode_number,
        )

        if len(state.content.talk) >= (len(state.preparation.questions) * 2) + 10:
            log.warning("Talk ended because too many messages have been generated.")
            return END

        if state.content.moderator_is_finished and state.content.guest_is_finished:
            log.info(" => Finished interview graph.")
            return END

        if len(state.content.talk) == 0:
            log.info(" => Moderator should talk.")
            return Nodes.MODERATOR

        last_message = state.content.talk[-1]
        if last_message.role == InterviewRoles.MODERATOR:
            log.info(" => Guest should talk.")
            return Nodes.GUEST

        elif last_message.role == InterviewRoles.GUEST:
            log.info(" => Moderator should talk.")
            return Nodes.MODERATOR

        raise ValueError(f"Unknown role: {last_message.role}")
