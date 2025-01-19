from pydantic import BaseModel

from talking_agents.graph.common.setup import PodcastSetup
from talking_agents.graph.common.preparation_content import PreparationContent


class PrepareState(BaseModel):
    setup: PodcastSetup
    content: PreparationContent
