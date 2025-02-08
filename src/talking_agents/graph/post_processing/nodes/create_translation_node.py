from typeguard import typechecked
import logging

from src.talking_agents.graph import INode
from src.talking_agents.graph.post_processing import PostProcessingState, Languages
from src.talking_agents.graph.common.interview_content import Message

log = logging.getLogger(__name__)


class CreateTranslationNode(INode[PostProcessingState]):
    @typechecked()
    def __init__(self):
        pass

    @typechecked()
    async def run(self, state: PostProcessingState) -> PostProcessingState:
        log.info("** POST-PROCESSING: CREATE TRANSLATION **")
        if state.content.language == Languages.ENGLISH:
            # since everything is already in english, no translation is necessary!
            state.content.interview = [
                Message(role=m.role, text=m.text) for m in state.interview.talk
            ]

        else:
            # ToDo: Implement translation here!
            raise NotImplementedError("Only ENGLISH is implemented yet!")

        return state
