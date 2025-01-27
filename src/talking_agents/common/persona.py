from pydantic import BaseModel, Field
from pathlib import Path
import yaml

from talking_agents.common.languages import Languages
from talking_agents.common import VoiceConfig


class Persona(BaseModel):
    name: str
    role_description: str
    additional_information: list[str]
    # noinspection PyDataclass
    private_additional_information: list[str] = Field(default_factory=list)
    voice: dict[Languages, VoiceConfig]

    @classmethod
    def from_file(cls, file_path: Path) -> "Persona":
        with file_path.open("r") as f:
            data = yaml.safe_load(f)
        data["voice"] = {
            Languages(language): VoiceConfig(**voice_settings) for language, voice_settings in data["voice"].items()
        }
        return cls(**data)

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
