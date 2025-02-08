from pydantic import BaseModel

from src.talking_agents.graph.common.setup import PodcastSetup
from src.talking_agents.graph.common.preparation_content import PreparationContent, Topic


class GenerateTopicsState(BaseModel):
    setup: PodcastSetup
    preparation: PreparationContent
    raw_topics: list[Topic] | None = None
    final_topics: list[Topic] | None = None
