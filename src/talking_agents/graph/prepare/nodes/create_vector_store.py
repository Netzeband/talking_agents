from typeguard import typechecked
from copy import deepcopy
from uuid import uuid4
import logging
from langchain_experimental.text_splitter import SemanticChunker
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage

from talking_agents.graph.common.prompt import load_prompt
from talking_agents.graph import INode
from talking_agents.graph.prepare.prepare_state import PrepareState
from talking_agents.common.vector_store import VectorStore, Chunk
from talking_agents.document.section import Section, ImageSection

log = logging.getLogger(__name__)


class CreateVectorStore(INode[PrepareState]):
    @typechecked()
    def __init__(
            self,
            llm: BaseChatModel,
            vector_store: VectorStore,
            text_splitter: SemanticChunker,
    ):
        self._llm = llm
        self._vector_store = vector_store
        self._text_splitter = text_splitter

    @typechecked()
    async def run(self, state: PrepareState) -> PrepareState:
        log.info("** PREPARE: CREATE VECTOR STORE **")
        vector_store_path = state.setup.episode_output_dir / "vector_store"
        if vector_store_path.exists():
            log.info(f"Loaded vector store from '{vector_store_path}'.")
            self._vector_store.load(vector_store_path)

        else:
            log.info(f"Create new vector store from document.")
            self._vector_store.create_from_documents(
                await self._get_chunks(state.setup.document, state.content.image_descriptions)
            )
            log.info(f"Save vector store to '{vector_store_path}'.")
            self._vector_store.save(vector_store_path)

        state.content.vector_store_entries = self._vector_store.get_number_of_entries()
        return state

    @typechecked()
    async def _get_chunks(
            self,
            document: list[Section],
            image_descriptions: dict[str, str],
    ) -> dict[str, Chunk]:
        document = deepcopy(document)
        for section in document:
            if isinstance(section, ImageSection):
                description = image_descriptions.get(str(section.path), None)
                if description is not None:
                    section.text = description

        text = "".join([section.text for section in document])
        return {
            str(uuid4()): Chunk(
                document=c,
                summary=await self._create_summary(c.page_content)
            ) for c in self._text_splitter.create_documents([text])
        }

    @typechecked()
    async def _create_summary(self, text: str) -> str:
        prompt = ChatPromptTemplate([
            (
                "system",
                load_prompt("prepare", "find_summary").render()
            ),
            MessagesPlaceholder("text"),
        ])
        model = prompt | self._llm
        response = await model.ainvoke({
            "text": [HumanMessage(content=text)]
        })
        log.info(" * Generate summary: %s", response.content)
        return response.content
