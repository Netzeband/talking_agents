from typeguard import typechecked
from langchain_core.language_models import BaseChatModel
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field
import logging

from src.talking_agents.graph.common.prompt import load_prompt
from src.talking_agents.graph import INode
from src.talking_agents.graph.prepare import PrepareState
from src.talking_agents.common.vector_store import VectorStore

log = logging.getLogger(__name__)


TEXT_LENGTH = 5000


class CreateTitleNodeOutput(BaseModel):
    title: str | None = Field(..., description="The title of the document.")
    is_more_text_needed: bool = Field(..., description="Indicates, if more text is needed for finding the title.")


class CreateTitleNode(INode[PrepareState]):
    @typechecked()
    def __init__(self, llm: BaseChatModel, vector_store: VectorStore):
        self._llm = llm
        self._vector_store = vector_store

    @typechecked()
    async def run(self, state: PrepareState) -> PrepareState:
        log.info("** PREPARE: CREATE TITLE **")

        is_more_text_needed = True
        text_length = 0
        while is_more_text_needed:
            text_length += TEXT_LENGTH
            prompt = ChatPromptTemplate.from_messages([
                (
                    "system",
                    "{system_prompt}"
                ),
                MessagesPlaceholder("document"),
            ])
            model = prompt | self._llm.with_structured_output(CreateTitleNodeOutput)
            message = HumanMessage(
                content=self._get_title_extraction_content(self._vector_store.get_text_content(), text_length),
            )
            response: CreateTitleNodeOutput = await model.ainvoke({
                "system_prompt": load_prompt("prepare", "find_document_title").render(),
                "document": [message]
            })

            is_more_text_needed = response.is_more_text_needed

            if response.title is not None and response.title != "":
                log.info(" * Found title: %s", response.title)
                state.content.title = response.title

            else:
                log.info("No title could be found. Give more text ...")
                is_more_text_needed = True
                state.content.title = None

        return state

    @staticmethod
    @typechecked()
    def _get_title_extraction_content(content: dict[str, str], text_length: int) -> list[dict[str, str]]:
        document_starting = ""
        for element in content.values():
            document_starting += element
            if len(document_starting) > text_length:
                break

        return [{"type": "text", "text": document_starting}]
