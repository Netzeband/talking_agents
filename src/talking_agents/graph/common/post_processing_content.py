from pydantic import BaseModel
from pathlib import Path, PurePosixPath
from typeguard import typechecked

from src.talking_agents.common.textwrap import textwrap
from src.talking_agents.common.languages import Languages, get_language_name
from src.talking_agents.graph.common.interview_content import Message


class VideoCreationContent(BaseModel):
    processed_audio_file: Path
    podcast_audio_file: Path
    podcast_video_file: Path

    def exists(self):
        return (self.processed_audio_file.exists() and
                self.podcast_audio_file.exists() and
                self.podcast_video_file.exists())


class PostProcessingContentVariant(BaseModel):
    language: Languages
    interview: list[Message] | None = None
    full_teaser: str | None = None
    core_teaser: str | None = None
    markdown_path: PurePosixPath | None = None
    teaser_markdown_path: PurePosixPath | None = None
    audio_adapted_interview: list[Message] | None = None
    audio_path: PurePosixPath | None = None
    video: VideoCreationContent | None = None

    @property
    def output_path(self) -> PurePosixPath:
        return PurePosixPath(f"output_{self.language.value}")

    def store(self, output_path: Path, episode_number):
        content_path = output_path / f"episode_{episode_number}"
        content_path.mkdir(parents=True, exist_ok=True)
        with open(content_path / f"post_processing_content_{self.language.value}.json", "w", encoding="utf-8") as file:
            file.write(self.model_dump_json(indent=4))

    @classmethod
    @typechecked()
    def load(cls, input_path: Path, episode_number: int, language: Languages) -> "PostProcessingContentVariant":
        content_path = input_path / f"episode_{episode_number}"
        try:
            with open(content_path / f"post_processing_content_{language.value}.json", "r", encoding="utf-8") as file:
                model = cls.model_validate_json(file.read())
                return model

        except FileNotFoundError:
            return cls(language=language)

    def __str__(self) -> str:
        content_string = ""
        content_string += f"* Interview: {self._get_talk_string(self.interview)}\n"
        content_string += f"* Teaser: {textwrap("\n" + str(self.full_teaser), prefix="  ", width=100)}\n"
        content_string += f"* Markdown File: {self.markdown_path}\n"
        content_string += f"* Is Interview adapted for Audio: {True if self.audio_adapted_interview else False}\n"
        content_string += f"* Raw Audio File: {self.audio_path}\n"
        content_string += f"* Podcast Video File: {self._get_video_path()}\n"
        return content_string

    @typechecked()
    def _get_video_path(self) -> str:
        return str(self.video.podcast_video_file.absolute()) if self.video is not None else 'None'

    @staticmethod
    @typechecked()
    def _get_talk_string(talk: list[Message] | None) -> str:
        if talk is None or len(talk) == 0:
            return "None"

        content_string = "\n"
        for message in talk:
            content_string += (f"_{message.role.value.upper()}_: "
                               f"{textwrap("\n" + message.text, prefix="  ", width=100)}\n")

            if message.metadata is not None:
                if ("groundedness" in message.metadata and
                        message.metadata["groundedness"] is not None and
                        "grounded_score" in message.metadata["groundedness"]
                ):
                    content_string += f"  _GROUNDED-SCORE_: {message.metadata["groundedness"]["grounded_score"]:.2f}\n"

                if ("redundancy" in message.metadata and
                        message.metadata["redundancy"] is not None and
                        "redundancy_score" in message.metadata["redundancy"]
                ):
                    content_string += f"  _REDUNDANCY-SCORE_: {message.metadata["redundancy"]["redundancy_score"]:.2f}\n"

        return content_string


class PostProcessingContent(BaseModel):
    variant: dict[Languages, PostProcessingContentVariant]

    def store(self, output_path: Path, episode_number: int):
        for language, variant in self.variant.items():
            variant.store(output_path, episode_number)

    @classmethod
    @typechecked()
    def load(cls, input_path: Path, episode_number: int, languages: list[Languages]) -> "PostProcessingContent":
        variants = {}
        for language in languages:
            variants[language] = PostProcessingContentVariant.load(input_path, episode_number, language)

        return cls(variant=variants)

    def __str__(self) -> str:
        content_string = ""
        for language, variant in self.variant.items():
            content_string += f"**** LANGUAGE: {get_language_name(language).upper()} ****\n"
            content_string += str(variant) + "\n"
        return content_string
