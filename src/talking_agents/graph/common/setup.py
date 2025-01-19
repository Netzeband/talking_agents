from pydantic import BaseModel, Field
from pathlib import PurePosixPath, Path
from datetime import datetime

from talking_agents.common import VoiceConfig
from talking_agents.document.section import Section
from talking_agents.graph.common.languages import Languages


class Persona(BaseModel):
    name: str
    role_description: str
    additional_information: list[str]
    # noinspection PyDataclass
    private_additional_information: list[str] = Field(default_factory=list)
    voice: dict[Languages, VoiceConfig]

    def get_role_description(self) -> str:
        return f"Your name is {self.name}. " + self.role_description

    def get_additional_information(self) -> str:
        additional_information = [f"Name: {self.name}"] + self.additional_information
        return "\n".join([f" * {info}" for info in additional_information])

    def get_private_additional_information(self) -> str:
        additional_information = [f"Name: {self.name}"]
        additional_information += self.additional_information
        additional_information += self.private_additional_information
        return "\n".join([f" * {info}" for info in additional_information])


class PodcastSetup(BaseModel):
    max_state: str
    date: datetime
    paper_url: str
    episode_number: int
    output_path: Path
    document_path: PurePosixPath
    document: list[Section]
    moderator: Persona
    guest: Persona
    languages: list[Languages]

    @property
    def episode_output_dir(self) -> Path:
        return self.output_path / f"episode_{self.episode_number}"
