from typeguard import typechecked
import logging

from talking_agents.graph import INode
from talking_agents.graph.main.state import State
from talking_agents.graph.post_processing import PostProcessingState
from talking_agents.common.languages import get_language_name

log = logging.getLogger(__name__)


class PostProcessingNode(INode[State]):
    @typechecked()
    def __init__(
            self,
            post_processing_graph: INode[PostProcessingState],
    ):
        self._post_processing_graph = post_processing_graph

    @typechecked()
    async def run(self, state: State) -> State:
        log.info("** POST-PROCESSING **.")
        for language in state.setup.languages:
            log.info(f"**** PROCESS LANGUAGE: {get_language_name(language).upper()} ****")
            result = PostProcessingState.model_validate(await self._post_processing_graph.run(
                PostProcessingState(
                    setup=state.setup,
                    preparation=state.content.preparation,
                    interview=state.content.interview,
                    content=state.content.post_processing.variant[language],
                )
            ))
            state.content.post_processing.variant[language] = result.content
        return state
