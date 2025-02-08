from pydantic import BaseModel, Field

from src.talking_agents.graph.common.setup import PodcastSetup
from src.talking_agents.graph.common.preparation_content import PreparationContent, Question


class PrepareQuestionState(BaseModel):
    setup: PodcastSetup
    preparation: PreparationContent
    expect_examples: bool
    topic: str
    answer_expectations: str
    previous_questions: list[Question]
    # noinspection PyDataclass
    current_questions: list[Question] = Field(default_factory=list)
    skip_and_continue: bool = False
    number_of_retries: int = 0
