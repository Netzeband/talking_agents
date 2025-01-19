from typeguard import typechecked
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import BaseMessage, HumanMessage
from pydantic import BaseModel, Field
import logging

from talking_agents.graph import INode
from talking_agents.graph.post_processing import PostProcessingState
from talking_agents.graph.common.languages import get_language_name
from talking_agents.graph.common.interview_content import Message, InterviewRoles
from talking_agents.graph.common.setup import PodcastSetup
from talking_agents.graph.common.prompt import load_prompt

log = logging.getLogger(__name__)


class CreateTeaserNodeOutput(BaseModel):
    teaser: str = Field(..., description="The teaser for the podcast episode.")


class CreateTeaserNode(INode[PostProcessingState]):
    @typechecked()
    def __init__(self, llm: BaseChatModel):
        self._llm = llm

    @typechecked()
    async def run(self, state: PostProcessingState) -> PostProcessingState:
        log.info("** POST-PROCESSING: CREATE TEASER **")
        prompt = ChatPromptTemplate.from_messages([
            ("system", "{system_prompt}"),
            MessagesPlaceholder("interview")
        ])
        model = prompt | self._llm.with_structured_output(CreateTeaserNodeOutput)
        response: CreateTeaserNodeOutput = await model.ainvoke({
            "system_prompt": load_prompt("post_processing", "create_teaser").render({
                "paper_title": state.preparation.title,
                "episode_number": state.setup.episode_number,
                "date": state.preparation.date.strftime("%A the %B %d, %Y"),
                "role_description": state.setup.moderator.get_role_description(),
                "guest_name": state.setup.guest.name,
                "language": get_language_name(state.content.language),
            }),
            "interview": self._get_interview(state.content.interview, state.setup),
        })
        state.content.core_teaser = response.teaser
        state.content.full_teaser = load_prompt(
            "post_processing",
            f"teaser_{state.content.language}"
        ).render({
            "teaser": state.content.core_teaser,
            "paper_title": state.preparation.title,
            "paper_url": state.setup.paper_url,
        })
        log.info(f" * Teaser: {state.content.full_teaser}")
        return state

    @staticmethod
    @typechecked()
    def _get_interview(interview: list[Message], setup: PodcastSetup) -> list[BaseMessage]:
        messages = []
        for message in interview:
            messages.append(
                HumanMessage(
                    content=message.text,
                    name=CreateTeaserNode._get_person_name(message.role, setup)
                )
            )

        # For the teaser we only need the beginning of the podcast!
        return messages[:4]

    @staticmethod
    @typechecked()
    def _get_person_name(role: InterviewRoles, setup: PodcastSetup) -> str:
        if role == InterviewRoles.MODERATOR:
            return setup.moderator.name
        elif role == InterviewRoles.GUEST:
            return setup.guest.name

        raise ValueError(f"Unknown interview role: {role}")
