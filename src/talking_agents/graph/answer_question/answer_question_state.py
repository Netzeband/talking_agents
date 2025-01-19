from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages
from typing import Annotated

from talking_agents.graph.common.setup import PodcastSetup
from talking_agents.graph.common.preparation_content import (
    PreparationContent, Question, Redundancy, Groundedness, FollowUp
)


class AnswerQuestionState(BaseModel):
    setup: PodcastSetup
    preparation: PreparationContent
    previous_questions: list[Question]

    original_question: str
    rephrased_question: str | None = None

    follow_up: FollowUp = Field(default_factory=FollowUp)

    intermediate_answer: str | None = None
    answers: list[str] | None = None

    groundedness: Groundedness = Field(default_factory=Groundedness)
    redundancy: Redundancy = Field(default_factory=Redundancy)

    tries: int = 1
    # noinspection PyDataclass
    messages: Annotated[list[BaseMessage], add_messages] = Field(default_factory=list)
    # noinspection PyDataclass
    sources: list[str] = Field(default_factory=list)
