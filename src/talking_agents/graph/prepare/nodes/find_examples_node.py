from typeguard import typechecked
from langchain_core.language_models import BaseChatModel
from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_core.documents import Document
import logging
import uuid

from src.talking_agents.graph.common.prompt import load_prompt
from src.talking_agents.graph import INode
from src.talking_agents.graph.prepare import PrepareState
from src.talking_agents.common.vector_store import VectorStore

log = logging.getLogger(__name__)


TEXT_LENGTH = 10000


class Example(BaseModel):
    text: str
    chunk_start_index: int
    chunk_end_index: int


class FindExamplesNodeOutput(BaseModel):
    # noinspection PyDataclass
    example_output: list[str] = Field(
        default_factory=list,
        description="The list of examples."
    )


class FindExamplesNode(INode[PrepareState]):
    @typechecked()
    def __init__(
            self,
            llm: BaseChatModel,
            vector_store: VectorStore,
            example_store: VectorStore,
    ):
        self._llm = llm
        self._vector_store = vector_store
        self._example_store = example_store

    @typechecked()
    async def run(self, state: PrepareState) -> PrepareState:
        log.info("** PREPARE: FIND EXAMPLES TITLE **")

        example_store_path = state.setup.episode_output_dir / "example_store"
        if example_store_path.exists():
            log.info(f"Loaded example store from '{example_store_path}'.")
            self._example_store.load(example_store_path)

        else:
            log.info(f"Create new example store from document.")
            self._example_store.create_from_documents(
                await self._get_chunks(
                    await self._get_examples_from_text()
                )
            )
            log.info(f"Save example store to '{example_store_path}'.")
            self._example_store.save(example_store_path)

        state.content.example_store_entries = self._example_store.get_number_of_entries()
        log.info(f"* Found {state.content.example_store_entries} examples")

        return state

    @typechecked()
    async def _get_chunks(
            self,
            examples: list[Example],
    ) -> dict[str, Document]:
        return {
            str(uuid.uuid4()): Document(
                page_content=e.text,
                metadata={"chunk_start_index": e.chunk_start_index, "chunk_end_index": e.chunk_end_index},
            ) for e in examples
        }

    @typechecked()
    async def _get_examples_from_text(self) -> list[Example]:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "{system_prompt}")
        ])
        model = prompt | self._llm.with_structured_output(FindExamplesNodeOutput)

        chunks = list(self._vector_store.get_text_content().values())
        examples = []
        chunk_text = ""

        chunk_start_index = None

        for i, text in enumerate(chunks):
            if chunk_start_index is None:
                chunk_start_index = i

            chunk_text += text
            if (len(chunk_text) < TEXT_LENGTH) and ((i + 1) < len(chunks)):
                continue
            chunk_end_index = i
            chunk_text = chunk_text + "..."

            log.info(f" * Find examples in chunk {i + 1}/{len(chunks)}")
            result: FindExamplesNodeOutput = await model.ainvoke({
                "system_prompt": load_prompt("prepare", "find_examples").render({
                    "text_piece": chunk_text,
                })
            })

            examples.extend([
                Example(
                    text=e,
                    chunk_start_index=chunk_start_index,
                    chunk_end_index=chunk_end_index
                ) for e in result.example_output
            ])
            # we need to keep 25% of the text to allow overlap
            keep_text_index = int(len(chunk_text) / 4)
            chunk_text = "..." + chunk_text[-keep_text_index:]
            chunk_start_index = None

        return examples
