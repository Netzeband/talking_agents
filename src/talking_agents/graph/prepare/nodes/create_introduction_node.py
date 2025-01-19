from typeguard import typechecked
from pydantic import BaseModel, Field
from langchain.prompts import ChatPromptTemplate
from langchain_core.language_models import BaseChatModel
import logging

from talking_agents.graph.common.prompt import load_prompt
from talking_agents.graph import INode
from talking_agents.graph.prepare.prepare_state import PrepareState

log = logging.getLogger(__name__)


class CreateIntroductionNodeOutput(BaseModel):
    introduction: str | None = Field(..., description="The introduction for the podcast.")


class CreateIntroductionNode(INode[PrepareState]):
    @typechecked()
    def __init__(self, llm: BaseChatModel):
        self._llm = llm

    @typechecked()
    async def run(self, state: PrepareState) -> PrepareState:
        log.info("** PREPARE: CREATE INTRODUCTION **")
        prompt = ChatPromptTemplate([
            ("system", load_prompt("prepare", "write_podcast_introduction").render(
                {
                    "role_description": state.setup.moderator.get_role_description(),
                    "paper_title": state.content.title,
                    "guest_info": state.setup.guest.get_additional_information(),
                    "date": state.setup.date.strftime("%A the %B %d, %Y"),
                    "episode_number": state.setup.episode_number,
                }
            )),
        ])
        model = prompt | self._llm.with_structured_output(CreateIntroductionNodeOutput)
        response = await model.ainvoke({})

        if response.introduction is not None and response.introduction != "":
            log.info(" * Introduction: %s", response.introduction)
            state.content.introduction = response.introduction

        else:
            log.error("Could not create an introduction.")
            state.content.introduction = None

        return state
