from typeguard import typechecked
from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate
import logging

from talking_agents.graph.common.prompt import load_prompt
from talking_agents.graph import INode
from talking_agents.graph.prepare import PrepareState
from talking_agents.common.vector_store import VectorStore

log = logging.getLogger(__name__)


TEXT_LENGTH = 5000


class CreateSummaryNode(INode[PrepareState]):
    @typechecked()
    def __init__(self, llm: BaseChatModel, vector_store: VectorStore):
        self._llm = llm
        self._vector_store = vector_store

    @typechecked()
    async def run(self, state: PrepareState) -> PrepareState:
        log.info("** PREPARE: CREATE SUMMARY **")

        chunks = list(self._vector_store.get_text_content().values())
        summary = ""
        text_length = TEXT_LENGTH
        chunk_text = ""
        for i, content in enumerate(chunks):
            chunk_text += content
            if (len(chunk_text) < text_length) and ((i + 1) < len(chunks)):
                continue
            log.info(" * Generate summary for chunks up to %s/%s", i + 1, len(chunks))

            prompt = ChatPromptTemplate.from_messages([
                (
                    "system",
                    "{system_prompt}"
                ),
            ])
            model = prompt | self._llm | StrOutputParser()
            response = await model.ainvoke({
                "system_prompt": load_prompt("prepare", "create_summary").render({
                    "old_summary": summary,
                    "new_context": chunk_text,
                }),
            })
            chunk_text = ""
            summary = response

        log.info(" * Summary: %s", summary)
        state.content.summary = summary

        return state
