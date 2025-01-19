from typeguard import typechecked
from langchain_core.language_models import BaseChatModel
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field
import logging

from talking_agents.document.section import Section, TextSection
from talking_agents.graph.common.prompt import load_prompt
from talking_agents.graph import INode
from talking_agents.graph.prepare import PrepareState

log = logging.getLogger(__name__)


class CreateTitleNodeOutput(BaseModel):
    title: str | None = Field(..., description="The title of the document.")


class CreateTitleNode(INode[PrepareState]):
    @typechecked()
    def __init__(self, llm: BaseChatModel):
        self._llm = llm

    @typechecked()
    async def run(self, state: PrepareState) -> PrepareState:
        log.info("** PREPARE: CREATE TITLE **")

        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                load_prompt("prepare", "find_document_title").render()
            ),
            MessagesPlaceholder("document"),
        ])
        model = prompt | self._llm.with_structured_output(CreateTitleNodeOutput)
        message = HumanMessage(
            content=self._get_title_extraction_content(state.setup.document),
        )
        response = await model.ainvoke({"document": [message]})

        if response.title is not None and response.title != "":
            log.info(" * Found title: %s", response.title)
            state.content.title = response.title

        else:
            log.warning("No title was extracted from the document: %s", message)
            state.content.title = None

        return state

    @staticmethod
    @typechecked()
    def _get_title_extraction_content(document: list[Section]) -> list[dict[str, str]]:
        document_starting = ""
        for section in document:
            if isinstance(section, TextSection):
                document_starting += section.text

            if len(document_starting) > 1000:
                break

        return [{"type": "text", "text": document_starting}]
