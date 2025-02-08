from pydantic import BaseModel, Field
from pathlib import Path

from src.talking_agents.graph.common.setup import PodcastSetup
from src.talking_agents.common import Languages
from src.talking_agents.graph.common.preparation_content import PreparationContent
from src.talking_agents.graph.common.interview_content import InterviewContent
from src.talking_agents.graph.common.post_processing_content import PostProcessingContent


class PodcastContent(BaseModel):
    preparation: PreparationContent = Field(default_factory=PreparationContent)
    interview: InterviewContent = Field(default_factory=InterviewContent)
    post_processing: PostProcessingContent = Field(default_factory=PostProcessingContent)

    def store(self, output_path: Path, episode_number: int):
        self.preparation.store(output_path, episode_number)
        self.interview.store(output_path, episode_number)
        self.post_processing.store(output_path, episode_number)

    @classmethod
    def load(cls, input_path: Path, episode_number: int, languages: list[Languages]) -> "PodcastContent":
        return cls(
            preparation=PreparationContent.load(input_path, episode_number),
            interview=InterviewContent.load(input_path, episode_number),
            post_processing=PostProcessingContent.load(input_path, episode_number, languages)
        )

    def __str__(self) -> str:
        content_string = "** PREPARATION **\n"
        content_string += str(self.preparation) + "\n"
        content_string += "** INTERVIEW **\n"
        content_string += str(self.interview) + "\n"
        content_string += "** POST PROCESSING **\n"
        content_string += str(self.post_processing) + "\n"
        return content_string


class State(BaseModel):
    setup: PodcastSetup
    content: PodcastContent = Field(default_factory=PodcastContent)
