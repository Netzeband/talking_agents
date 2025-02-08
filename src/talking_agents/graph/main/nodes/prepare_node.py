from typeguard import typechecked
import logging

from src.talking_agents.graph import INode
from src.talking_agents.graph.main.state import State
from src.talking_agents.graph.prepare import PrepareState

log = logging.getLogger(__name__)


class PrepareNode(INode[State]):
    @typechecked()
    def __init__(
            self,
            prepare_graph: INode[PrepareState],
    ):
        self._prepare_graph = prepare_graph

    @typechecked()
    async def run(self, state: State) -> State:
        log.info("** PREPARE **.")
        # permanently store the date of the first run
        if state.content.preparation.date is None:
            state.content.preparation.date = state.setup.date
        result = PrepareState.model_validate(await self._prepare_graph.run(
            PrepareState(
                setup=state.setup,
                content=state.content.preparation,
            )
        ))
        state.content.preparation = result.content
        return state
