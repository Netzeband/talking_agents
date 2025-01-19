from typeguard import typechecked
from abc import ABC, abstractmethod
from pathlib import Path
from pydantic import BaseModel, Field


class VoiceConfig(BaseModel):
    ssml: str = Field(
        ...,
        description="A SSML string, which describes the voice and contains a \"{text}\" placeholder."
    )


class SpeechText(BaseModel):
    text: str
    voice_config: VoiceConfig
    is_escaped: bool = False


class SpeechEngineError(Exception):
    pass


class ISpeechEngine(ABC):
    @typechecked()
    @abstractmethod
    def text_to_file(self, text: list[SpeechText], file: Path):
        raise NotImplementedError
