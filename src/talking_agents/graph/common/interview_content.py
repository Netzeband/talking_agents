from pydantic import BaseModel, Field
from enum import StrEnum
from pathlib import Path

from talking_agents.common import textwrap


class InterviewRoles(StrEnum):
    MODERATOR = 'moderator'
    GUEST = 'guest'


class Message(BaseModel):
    text: str
    role: InterviewRoles
    # noinspection PyDataclass
    metadata: dict = Field(default_factory=dict)


class InterviewContent(BaseModel):
    # noinspection PyDataclass
    talk: list[Message] = Field(default_factory=list)
    # if next question is -1, it is the introduction and if next question is greater than the number of prepared
    #  questions, it is the wrap-up
    next_question: int = -1
    moderator_is_finished: bool = False
    guest_is_finished: bool = False

    def store(self, output_path: Path, episode_number: int):
        content_path = output_path / f"episode_{episode_number}"
        content_path.mkdir(parents=True, exist_ok=True)
        with open(content_path / "interview_content.json", "w", encoding="utf-8") as file:
            file.write(self.model_dump_json(indent=4))

    @classmethod
    def load(cls, input_path: Path, episode_number: int) -> "InterviewContent":
        content_path = input_path / f"episode_{episode_number}"
        try:
            with open(content_path / "interview_content.json", "r", encoding="utf-8") as file:
                model = cls.model_validate_json(file.read())
                return model

        except FileNotFoundError:
            return cls()

    def __str__(self) -> str:
        content_string = ""
        content_string += f"* Talk: {self._get_talk_string(self.talk)}\n"
        content_string += f"* Moderator is finished: {self.moderator_is_finished}\n"
        content_string += f"* Guest is finished: {self.moderator_is_finished}\n"
        return content_string

    @staticmethod
    def _get_talk_string(talk: list[Message]) -> str:
        if len(talk) == 0:
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
