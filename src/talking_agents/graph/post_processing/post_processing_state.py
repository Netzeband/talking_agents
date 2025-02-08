from pydantic import BaseModel

from src.talking_agents.graph.common.setup import PodcastSetup
from src.talking_agents.graph.common.interview_content import InterviewContent
from src.talking_agents.graph.common.preparation_content import PreparationContent
from src.talking_agents.graph.common.post_processing_content import PostProcessingContentVariant, Languages


class PostProcessingState(BaseModel):
    setup: PodcastSetup
    preparation: PreparationContent
    interview: InterviewContent
    content: PostProcessingContentVariant
