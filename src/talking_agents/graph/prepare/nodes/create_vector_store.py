from typeguard import typechecked
from uuid import uuid4
import logging
from langchain_core.language_models import BaseChatModel
from unstructured.documents.elements import Element, Table, Image, NarrativeText
from unstructured.chunking.title import chunk_by_title
from langchain_core.documents import Document

from src.talking_agents.graph import INode
from src.talking_agents.graph.prepare.prepare_state import PrepareState
from src.talking_agents.common.vector_store import VectorStore
from src.talking_agents.common.document_store import DocumentStore

log = logging.getLogger(__name__)


class CreateVectorStore(INode[PrepareState]):
    @typechecked()
    def __init__(
            self,
            llm: BaseChatModel,
            vector_store: VectorStore,
            document_store: DocumentStore,
    ):
        self._llm = llm
        self._vector_store = vector_store
        self._document_store = document_store

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
                await self._get_chunks(
                    self._document_store.get_elements(),
                    state.content.image_descriptions,
                    state.content.table_descriptions,
                )
            )
            log.info(f"Save vector store to '{vector_store_path}'.")
            self._vector_store.save(vector_store_path)

        state.content.vector_store_entries = self._vector_store.get_number_of_entries()
        return state

    @typechecked()
    async def _get_chunks(
            self,
            elements: list[Element],
            image_descriptions: dict[str, str],
            table_descriptions: dict[str, str],
    ) -> dict[str, Document]:
        new_elements = []
        for element in elements:
            if isinstance(element, Image):
                new_elements.append(self._substitute_element(element, image_descriptions))

            elif isinstance(element, Table):
                new_elements.append(self._substitute_element(element, table_descriptions))

            else:
                new_elements.append(element)

        chunks = chunk_by_title(
            new_elements,
            include_orig_elements=False,
            multipage_sections=True,
            overlap=100,
            overlap_all=False,
        )

        return {
            str(uuid4()): Document(
                page_content=str(c.text), metadata=self._get_metadata_for_chunk(c)
            ) for c in chunks
        }

    @staticmethod
    @typechecked()
    def _substitute_element(element: Image | Table, substitution: dict[str, str]) -> Element:
        description = substitution.get(element.id, None)
        if description is not None:
            return NarrativeText(
                text=description,
                element_id=element.id,
                coordinates=None,
                coordinate_system=None,
                metadata=element.metadata,
                detection_origin=None,
                embeddings=element.embeddings,
            )
        return element

    @staticmethod
    @typechecked()
    def _get_metadata_for_chunk(chunk: Element) -> dict:
        metadata = chunk.metadata.to_dict()
        metadata.update({
            "element_id": chunk.id,
            "category": chunk.category,
        })
        return metadata
