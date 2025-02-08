from pydantic import BaseModel

from src.talking_agents.graph.common.setup import PodcastSetup
from src.talking_agents.graph.common.preparation_content import PreparationContent


class PrepareState(BaseModel):
    setup: PodcastSetup
    content: PreparationContent
