from pydantic import BaseModel, Field

from talking_agents.graph.common.setup import PodcastSetup
from talking_agents.graph.common.preparation_content import PreparationContent
from talking_agents.graph.common.interview_content import InterviewContent


class InterviewState(BaseModel):
    setup: PodcastSetup
    preparation: PreparationContent
    content: InterviewContent = Field(default_factory=InterviewContent)
