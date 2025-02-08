from typeguard import typechecked
import logging
from pydantic import BaseModel, Field
from langchain.prompts import ChatPromptTemplate
from langchain_core.language_models import BaseChatModel

from src.talking_agents.graph.common.prompt import load_prompt
from src.talking_agents.graph import INode
from src.talking_agents.graph.prepare.prepare_state import PrepareState

log = logging.getLogger(__name__)


class CreateWrapUpNodeOutput(BaseModel):
    wrapup: str | None = Field(..., description="The wrap-up for the podcast.")


class CreateWrapUpNode(INode[PrepareState]):
    @typechecked
    def __init__(self, llm: BaseChatModel):
        self._llm = llm

    @typechecked()
    async def run(self, state: PrepareState) -> PrepareState:
        log.info("** PREPARE: CREATE WRAP UP **")
        prompt = ChatPromptTemplate([
            ("system", load_prompt("prepare", "write_podcast_wrapup").render(
                {
                    "role_description": state.setup.moderator.get_role_description(),
                    "paper_title": state.content.title,
                    "guest_info": state.setup.guest.get_additional_information(),
                    "episode_number": state.setup.episode_number,
                }
            )),
        ])
        model = prompt | self._llm.with_structured_output(CreateWrapUpNodeOutput)
        response = await model.ainvoke({})

        if response.wrapup is not None and response.wrapup != "":
            log.info(" * Wrap-up: %s", response.wrapup)
            state.content.wrapup = response.wrapup

        else:
            log.error("Could not create a wrap-up.")
            state.content.wrapup = None

        return state
