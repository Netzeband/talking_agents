from pydantic import BaseModel, Field
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage
from typeguard import typechecked
from typing import Any
import logging
import base64
from unstructured.documents.elements import Image, Element, NarrativeText

from talking_agents.graph.common.prompt import load_prompt
from talking_agents.graph import INode
from talking_agents.graph.prepare.prepare_state import PrepareState
from talking_agents.common.document_store import DocumentStore

log = logging.getLogger(__name__)


class CreateImageDescriptionsNodeOutput(BaseModel):
    description: str | None = Field(..., description="The description of the image.")


class CreateImageDescriptionsNode(INode[PrepareState]):
    @typechecked()
    def __init__(
            self,
            llm: BaseChatModel,
            document_store: DocumentStore,
    ):
        self._llm = llm
        self._document_store = document_store

    @typechecked()
    async def run(self, state: PrepareState) -> PrepareState:
        log.info("** PREPARE: CREATE IMAGE DESCRIPTIONS **")
        document_elements = self._document_store.get_elements()

        image_descriptions = {}
        for i, element in enumerate(document_elements):
            if isinstance(element, Image):
                image_descriptions[element.id] = await self._run_singe_image(document_elements, i)
                log.info(
                    "Image description for '%s': %s",
                    element.id,
                    image_descriptions[element.id]
                )

        state.content.image_descriptions = image_descriptions
        return state

    @typechecked()
    async def _run_singe_image(self, document: list[Element], image_index: int) -> str:
        prompt = ChatPromptTemplate([
            ("system", "{system_prompt}"),
            MessagesPlaceholder("document"),
        ])
        model = prompt | self._llm.with_structured_output(CreateImageDescriptionsNodeOutput)
        response = await model.ainvoke({
            "system_prompt": load_prompt("prepare", "find_image_description").render({}),
            "document": [
                HumanMessage(content=self._get_image_and_surrounding_text(
                    document,
                    image_index,
                    1000
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
            document: list[Element],
            image_index: int,
            text_length: int
    ) -> list[dict[str, Any]]:
        elements_before = self._limit_reverse_section_text(document[:image_index], text_length)
        elements_after = self._limit_section_text(document[image_index:], text_length)
        image_element = document[image_index]
        elements_to_consider = elements_before + [image_element] + elements_after

        output = []
        for element in elements_to_consider:
            if isinstance(element, Image):
                output.append({
                    "type": "image_url",
                    "image_url": { "url": self._get_base64_image(element) }
                })
            else:
                output.append({"type": "text", "text": element.text})
        return output

    @staticmethod
    @typechecked()
    def _limit_section_text(elements: list[Element], text_length: int) -> list[Element]:
        text = ""
        output_elements = []
        for element in elements:
            if len(text) + len(element.text) <= text_length:
                text += element.text
                output_elements.append(element)

            else:
                remaining_length = text_length - len(text)
                remaining_section_text = element.text[:remaining_length] + "..."
                output_elements.append(NarrativeText(
                    text=remaining_section_text,
                    element_id=element.id,
                    metadata=element.metadata,
                ))
                break

        return output_elements

    @staticmethod
    @typechecked()
    def _limit_reverse_section_text(elements: list[Element], text_length: int) -> list[Element]:
        text = ""
        output_elements: list[Element] = []
        for element in reversed(elements):
            if len(text) + len(element.text) <= text_length:
                text += element.text
                output_elements.append(element)

            else:
                remaining_length = text_length - len(text)
                remaining_section_text = "..." + element.text[-remaining_length:]
                output_elements.append(NarrativeText(
                    text=remaining_section_text,
                    element_id=element.id,
                    metadata=element.metadata,
                ))
                break

        return list(reversed(output_elements))

    @staticmethod
    @typechecked()
    def _get_base64_image(image: Image) -> str:
        base64_image = image.metadata.image_base64
        mime_type = image.metadata.image_mime_type
        embedded_image = f"data:{mime_type};base64,{base64_image}"
        return embedded_image
