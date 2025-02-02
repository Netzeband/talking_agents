from typeguard import typechecked
import logging

from talking_agents.graph import INode
from talking_agents.graph.prepare.prepare_state import PrepareState
from talking_agents.graph.generate_topics import GenerateTopicsState

log = logging.getLogger(__name__)


class GenerateTopicsNode(INode[PrepareState]):
    @typechecked()
    def __init__(
            self,
            generate_topics_graph: INode[GenerateTopicsState]
    ):
        self._generate_topics_graph = generate_topics_graph

    @typechecked()
    async def run(self, state: PrepareState) -> PrepareState:
        log.info("** PREPARE: CREATE TOPICS **")

        result = GenerateTopicsState.model_validate(await self._generate_topics_graph.run(
            GenerateTopicsState(
                setup=state.setup,
                preparation=state.content,
            )
        ))

        state.content.topics = result.final_topics
        return state
