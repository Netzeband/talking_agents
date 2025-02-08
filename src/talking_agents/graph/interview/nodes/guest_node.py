from typeguard import typechecked
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
import logging

from src.talking_agents.graph import INode
from src.talking_agents.graph.interview.interview_state import InterviewState
from src.talking_agents.graph.common.interview_content import Message, InterviewRoles
from src.talking_agents.graph.guest.guest_state import GuestState

log = logging.getLogger(__name__)


class GuestNode(INode[InterviewState]):
    @typechecked()
    def __init__(self, guest_graph: INode[GuestState], min_accepted_grounded_score: float):
        self._guest_graph = guest_graph
        self._min_accepted_grounded_score = min_accepted_grounded_score

    @typechecked()
    async def run(self, state: InterviewState) -> InterviewState:
        log.info("** INTERVIEW: GUEST **")
        result = GuestState.model_validate(await self._guest_graph.run(
            GuestState(
                setup=state.setup,
                preparation=state.preparation,
                history=self._create_history(state.content.talk),
                is_moderator_finished=state.content.moderator_is_finished,
                next_question=state.content.next_question,
            )
        ))
        state.content.talk.append(
            Message(
                role=InterviewRoles.GUEST,
                text=result.answer,
                metadata={
                    "topic": result.topic,
                    "sources": result.sources,
                    "redundancy":
                        result.answer_redundancy.model_dump() if result.answer_redundancy is not None else None,
                    "groundedness":
                        result.answer_groundedness.model_dump() if result.answer_groundedness is not None else None,
                }
            )
        )
        state.content.next_question += 1
        if result.is_finished:
            log.info(" => Guest finished the interview.")
            state.content.guest_is_finished = result.is_finished
        return state

    @typechecked()
    def _create_history(self, talk: list[Message]) -> list[BaseMessage]:
        history = []
        for message in talk:
            if message.role == InterviewRoles.GUEST:
                history.append(AIMessage(content=message.text))
            else:
                history.append(HumanMessage(content=message.text))
        return history
