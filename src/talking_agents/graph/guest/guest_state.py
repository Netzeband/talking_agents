from typing import Annotated
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages

from talking_agents.graph.common.setup import PodcastSetup
from talking_agents.graph.common.preparation_content import PreparationContent, Redundancy, Groundedness


class GuestState(BaseModel):
    setup: PodcastSetup
    preparation: PreparationContent
    history: Annotated[list[BaseMessage], add_messages]
    is_moderator_finished: bool
    # -1 means introduction question, greater than number of questions means wrap-up question
    next_question: int
    topic: str | None = None
    # noinspection PyDataclass
    messages: Annotated[list[BaseMessage], add_messages] = Field(default_factory=list)
    # noinspection PyDataclass
    sources: list[str] = Field(default_factory=list)
    answer_redundancy: Redundancy | None = None
    answer_groundedness: Groundedness | None = None
    answer: str | None = None
    is_finished: bool = False
