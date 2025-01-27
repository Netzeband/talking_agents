from typeguard import typechecked
from pydantic import BaseModel, AnyUrl
from pathlib import Path
import yaml

from .persona import Persona
from .languages import Languages


class EpisodeConfig(BaseModel):
    episode_number: int
    document_path: Path
    paper_url: AnyUrl
    moderator_persona: Persona
    guest_persona: Persona
    languages: list[Languages]

    @classmethod
    @typechecked()
    def from_file(cls, file_path: Path) -> "EpisodeConfig":
        base_path = file_path.parent
        with file_path.open("r") as f:
            data = yaml.safe_load(f)
        data["document_path"] = (base_path / data["document_path"]).absolute()
        data["moderator_persona"] = Persona.from_file(base_path / data["moderator_persona"])
        data["guest_persona"] = Persona.from_file(base_path / data["guest_persona"])
        data["languages"] = [Languages(l) for l in data["languages"]]
        return cls(**data)
