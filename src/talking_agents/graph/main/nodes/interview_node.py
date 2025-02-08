from typeguard import typechecked
import logging

from src.talking_agents.graph import INode
from src.talking_agents.graph.main.state import State
from src.talking_agents.graph.interview import InterviewState

log = logging.getLogger(__name__)


class InterviewNode(INode[State]):
    @typechecked()
    def __init__(
            self,
            interview_graph: INode[InterviewState],
    ):
        self._interview_graph = interview_graph

    @typechecked()
    async def run(self, state: State) -> State:
        log.info("** INTERVIEW **.")
        result = InterviewState.model_validate(await self._interview_graph.run(
            InterviewState(
                setup=state.setup,
                preparation=state.content.preparation,
                content=state.content.interview,
            )
        ))
        state.content.interview = result.content
        return state
