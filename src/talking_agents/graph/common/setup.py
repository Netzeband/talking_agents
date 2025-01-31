from pydantic import BaseModel
from pathlib import PurePosixPath, Path
from datetime import datetime

from talking_agents.common import Persona, Languages


class PodcastSetup(BaseModel):
    document_path: Path | None = None
    max_state: str
    date: datetime
    paper_url: str
    episode_number: int
    output_path: Path
    moderator: Persona
    guest: Persona
    languages: list[Languages]

    @property
    def episode_output_dir(self) -> Path:
        return self.output_path / f"episode_{self.episode_number}"
