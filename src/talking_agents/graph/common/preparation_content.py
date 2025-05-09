from pydantic import BaseModel, Field
from pathlib import Path
from typing import Any
from datetime import datetime

from src.talking_agents.common import textwrap


class Redundancy(BaseModel):
    new_information: list[str] | None = None
    old_information: list[str] | None = None
    score: float | None = None


class Groundedness(BaseModel):
    grounded_information: list[str] | None = None
    ungrounded_information: list[str] | None = None
    score: float | None = None


class FollowUp(BaseModel):
    is_necessary: bool = False
    question: str | None = None
    follow_ups: int = 0


class Question(BaseModel):
    question: str
    topic: str
    answer: list[str] | None = None
    redundancy: Redundancy = Field(default_factory=Redundancy)
    groundedness: Groundedness = Field(default_factory=Groundedness)
    follow_up: FollowUp = Field(default_factory=FollowUp)
    # noinspection PyDataclass
    metadata: dict[str, Any] = Field(default_factory=dict)


class Topic(BaseModel):
    description: str
    answer_expectation: str
    reasoning: str
    original_topics: list[str] | None = None
    consolidation_reasoning: str | None = None

    def __str__(self) -> str:
        topic_string = ""
        topic_string += f"* {self.description}\n"
        if self.answer_expectation is not None:
            topic_string += f"  * Answer Expectation: {self.answer_expectation}\n"
        if self.reasoning is not None:
            topic_string += f"  * Reasoning: {self.reasoning}\n"
        if self.original_topics is not None:
            topic_string += f"  * Original Topics:\n{'\n'.join([f'    * {t}' for t in self.original_topics])}\n"
        if self.consolidation_reasoning is not None:
            topic_string += f"  * Consolidation Reasoning: {self.consolidation_reasoning}\n"
        return topic_string


class PreparationContent(BaseModel):
    input_file: Path | None = None
    date: datetime | None = None
    extracted_document_file: Path | None = None
    title: str | None = None
    summary: str | None = None
    introduction: str | None = None
    questions: list[Question] | None = None
    topics: list[Topic] | None = None
    # noinspection PyDataclass
    skipped_topics: list[str] = Field(default_factory=list)
    wrapup: str | None = None
    image_descriptions: dict[str, str] | None = None
    table_descriptions: dict[str, str] | None = None
    vector_store_entries: int | None = None
    example_store_entries: int | None = None

    def store(self, output_path: Path, episode_number: int):
        content_path = output_path / f"episode_{episode_number}"
        content_path.mkdir(parents=True, exist_ok=True)
        with open(content_path / "preparation_content.json", "w", encoding="utf-8") as file:
            file.write(self.model_dump_json(indent=4))

    @classmethod
    def load(cls, input_path: Path, episode_number: int) -> "PreparationContent":
        content_path = input_path / f"episode_{episode_number}"
        try:
            with open(content_path / "preparation_content.json", "r", encoding="utf-8") as file:
                model = cls.model_validate_json(file.read())
                return model

        except FileNotFoundError:
            return cls()

    def __str__(self) -> str:
        content_string = ""
        content_string += f"* Podcast Date: {self.date.strftime("%A the %B %d, %Y")}\n"
        content_string += f"* Paper Tile: {self.title}\n"
        content_string += f"* Paper Summary: {self._wrap_long_text(self.summary)}\n"
        content_string += f"* Image Descriptions: {self._get_descriptions(self.image_descriptions)}\n"
        content_string += f"* Table Descriptions: {self._get_descriptions(self.table_descriptions)}\n"
        content_string += f"* Vector Store Entries: {self.vector_store_entries}\n"
        content_string += f"* Introduction: {self._wrap_long_text(self.introduction)}\n"
        content_string += f"* Topics: {self._get_topics(self.topics)}\n"
        content_string += f"* Questions: {self._get_questions(self.questions)}\n"
        content_string += f"* Wrapup: {self._wrap_long_text(self.wrapup)}\n"
        return content_string

    def _get_descriptions(self, descriptions: dict[str, str] | None) -> str:
        if descriptions is None:
            return "None"
        return str(len(descriptions.keys()))

    def _get_topics(self, topics: list[Topic] | None) -> str:
        if topics is None:
            return "None\n"
        topics_string = "\n" + "".join([f"    {i+1}. {t.description}\n" for i, t in enumerate(topics)])
        return topics_string

    def _get_questions(self, questions: list[Question] | None) -> str:
        if questions is None:
            return "None\n"
        question_string = "\n"
        for i, question in enumerate(questions):
            question_string += textwrap(f"{i+1}. {question.question}", prefix="    ") + "\n"
            if question.answer:
                for answer in question.answer:
                    question_string += textwrap(f" *  {answer}", prefix="    ") + "\n"
            if question.redundancy.score is not None:
                question_string += f" * Redundancy: {question.redundancy.score * 100:.2f}%\n"
            if question.groundedness.score is not None:
                question_string += f" * Groundedness: {question.groundedness.score * 100:.2f}%\n"
        return question_string

    def _wrap_long_text(self, text: str | None) -> str:
        if text is None:
            return "None\n"
        return textwrap("\n" + text, prefix="    ")
