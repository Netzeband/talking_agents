from typeguard import typechecked
from langchain_core.messages import HumanMessage
from langchain_core.prompts import MessagesPlaceholder
from pydantic import BaseModel, Field
from langchain.prompts import ChatPromptTemplate
from langchain_core.language_models import BaseChatModel
import logging

from talking_agents.graph.common.prompt import load_prompt
from talking_agents.graph import INode
from talking_agents.graph.prepare.prepare_state import PrepareState
from talking_agents.graph.common.preparation_content import Topic as PreparationTopic

log = logging.getLogger(__name__)


class Topic(BaseModel):
    description: str = Field(
        ...,
        description="A short topic description"
    )
    answer_expectation: str = Field(
        ...,
        description="A short description about the expectations what the guest might answer here."
    )
    reasoning: str = Field(
        ...,
        description="A reason why this topic is important enough to discuss and why this topic in at this position."
    )


class CreateTopicsNodeOutput(BaseModel):
    topics: list[Topic] | None = Field(
        ...,
        description="A list of topics to talk about in the podcast episode for act 1."
    )


class CreateTopicsNode(INode[PrepareState]):
    @typechecked()
    def __init__(
            self,
            llm: BaseChatModel,
    ):
        self._llm = llm

    @typechecked()
    async def run(self, state: PrepareState) -> PrepareState:
        log.info("** PREPARE: CREATE TOPICS **")
        prompt = ChatPromptTemplate([
            ("system", "{system_prompt}"),
        ])
        model = prompt | self._llm.with_structured_output(CreateTopicsNodeOutput)
        response = await model.ainvoke({
            "system_prompt": load_prompt("prepare", "create_podcast_topics").render(
                {
                    "role_description": state.setup.moderator.get_role_description(),
                    "paper_title": state.content.title,
                    "summary": state.content.summary,
                }
            ),
        })

        topics = []
        topics.extend(response.topics)

        if len(topics) > 0:
            log.info(" * Topics: %s", len(topics))
            for topic in topics:
                log.info("   * %s", topic)
            state.content.topics = [
                PreparationTopic(**t.model_dump()) for t in topics
            ]

        else:
            log.error("Could not create topics.")
            state.content.topics = None

        return state
