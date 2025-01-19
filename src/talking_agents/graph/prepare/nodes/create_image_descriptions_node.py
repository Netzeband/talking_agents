from pathlib import PurePosixPath
from pydantic import BaseModel, Field
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage
from typeguard import typechecked
from typing import Any
import logging
import base64

from talking_agents.graph.common.prompt import load_prompt
from talking_agents.graph import INode
from talking_agents.graph.prepare.prepare_state import PrepareState
from talking_agents.document.section import ImageSection, Section, TextSection

log = logging.getLogger(__name__)


class CreateImageDescriptionsNodeOutput(BaseModel):
    description: str | None = Field(..., description="The description of the image.")


class CreateImageDescriptionsNode(INode[PrepareState]):
    @typechecked()
    def __init__(
            self,
            llm: BaseChatModel,
    ):
        self._llm = llm

    @typechecked()
    async def run(self, state: PrepareState) -> PrepareState:
        log.info("** PREPARE: CREATE IMAGE DESCRIPTIONS **")
        base_path = state.setup.document_path.parent
        document = state.setup.document

        image_descriptions = {}
        for i, section in enumerate(document):
            if isinstance(section, ImageSection):
                image_descriptions[str(section.path)] = await self._run_singe_image(base_path, document, i)
                log.info(
                    "Image description for '%s': %s",
                    section.path,
                    image_descriptions[str(section.path)]
                )

        state.content.image_descriptions = image_descriptions
        return state

    @typechecked()
    async def _run_singe_image(self, base_path: PurePosixPath, document: list[Section], image_index: int) -> str:
        prompt = ChatPromptTemplate([
            ("system", load_prompt("prepare", "find_image_description").render({})),
            MessagesPlaceholder("document"),
        ])
        model = prompt | self._llm.with_structured_output(CreateImageDescriptionsNodeOutput)
        response = await model.ainvoke({
            "document": [
                HumanMessage(content=self._get_image_and_surrounding_text(
                    base_path,
                    document,
                    image_index,
                    500
                ))
            ]
        })

        if response.description is not None and response.description != "":
            return response.description

        else:
            log.error("Could not create an image description.")
            return "No description for the image found."

    def _get_image_and_surrounding_text(
            self,
            base_path: PurePosixPath,
            document: list[Section],
            image_index: int,
            text_length: int
    ) -> list[dict[str, Any]]:
        sections_before = self._limit_reverse_section_text(document[:image_index], text_length)
        sections_after = self._limit_section_text(document[image_index:], text_length)
        image_section = document[image_index]
        sections_to_consider = sections_before + [image_section] + sections_after

        output = []
        for section in sections_to_consider:
            if isinstance(section, TextSection):
                output.append({"type": "text", "text": section.text})
            elif isinstance(section, ImageSection):
                output.append({
                    "type": "image_url",
                    "image_url": { "url": self._get_base64_image(base_path, section.path) }
                })
        return output

    @staticmethod
    @typechecked()
    def _limit_section_text(sections: list[Section], text_length: int) -> list[Section]:
        text = ""
        output_sections = []
        for section in sections:
            if isinstance(section, TextSection):
                if len(text) + len(section.text) <= text_length:
                    text += section.text
                    output_sections.append(section)

                else:
                    remaining_length = text_length - len(text)
                    remaining_section_text = section.text[:remaining_length]
                    output_sections.append(TextSection(text=remaining_section_text))
                    break

            else:
                output_sections.append(section)

        return output_sections

    @staticmethod
    @typechecked()
    def _limit_reverse_section_text(sections: list[Section], text_length: int) -> list[Section]:
        text = ""
        output_sections = []
        for section in reversed(sections):
            if isinstance(section, TextSection):
                if len(text) + len(section.text) <= text_length:
                    text += section.text
                    output_sections.append(section)

                else:
                    remaining_length = text_length - len(text)
                    remaining_section_text = section.text[-remaining_length:]
                    output_sections.append(TextSection(text=remaining_section_text))
                    break

            else:
                output_sections.append(section)

        return output_sections

    @staticmethod
    @typechecked()
    def _get_base64_image(base_path: PurePosixPath, image_path: PurePosixPath) -> str:
        full_path = base_path / image_path
        suffix = image_path.suffix[1:]
        with open(full_path, "rb") as file:
            image_bytes = file.read()
            base64_image = base64.b64encode(image_bytes).decode()
            embedded_image = f"data:image/{suffix};base64,{base64_image}"
            return embedded_image
