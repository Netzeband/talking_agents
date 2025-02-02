from typeguard import typechecked
from pydantic import BaseModel, Field
from langchain.prompts import ChatPromptTemplate
from langchain_core.language_models import BaseChatModel
import logging

from talking_agents.graph.common.prompt import load_prompt
from talking_agents.graph import INode
from talking_agents.graph.generate_topics import GenerateTopicsState
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
    original_topics: list[str] = Field(
        ...,
        description="A list of the original topics, which have been consolidated into this topics "
                    "(if a consolidation happened)"
    )
    consolidation_reasoning: str = Field(
        ...,
        description="A reason why the original topics have been consolidated with each other."
    )


class ReviewTopicsNodeOutput(BaseModel):
    topics: list[Topic] | None = Field(
        ...,
        description="A new list of topics which also contains the consolidated topics."
    )


class ReviewTopicsNode(INode[GenerateTopicsState]):
    @typechecked()
    def __init__(
            self,
            llm: BaseChatModel,
    ):
        self._llm = llm

    @typechecked()
    async def run(self, state: GenerateTopicsState) -> GenerateTopicsState:
        log.info("** GENERATE TOPICS: REVIEW TOPICS **")
        prompt = ChatPromptTemplate([
            ("system", "{system_prompt}"),
        ])
        model = prompt | self._llm.with_structured_output(ReviewTopicsNodeOutput)
        response: ReviewTopicsNodeOutput = await model.ainvoke({
            "system_prompt": load_prompt("generate_topics", "review_podcast_topics").render(
                {
                    "topics": "\n".join([str(t) for t in state.raw_topics]),
                }
            ),
        })

        topics = []
        topics.extend(response.topics)

        if len(topics) > 0:
            log.info(" * Final Topics: %s", len(topics))
            for topic in topics:
                log.info("   * %s", topic)
            state.final_topics = [
                PreparationTopic(**t.model_dump()) for t in topics
            ]

        else:
            log.error("Could not create topics.")
            state.final_topics = []

        return state
