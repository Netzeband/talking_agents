from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from typeguard import typechecked
import logging
import io
import pandas as pd
from unstructured.documents.elements import Element, Table, TableChunk
from langchain_experimental.agents import create_pandas_dataframe_agent

from talking_agents.graph.common.prompt import load_prompt
from talking_agents.graph import INode
from talking_agents.graph.prepare.prepare_state import PrepareState
from talking_agents.common.document_store import DocumentStore
from talking_agents.graph.prepare.common import get_surrounding_document_elements

log = logging.getLogger(__name__)


class CreateTableDescriptionsNodeOutput(BaseModel):
    description: str | None = Field(..., description="The description of the table.")


class CreateTableDescriptionsNode(INode[PrepareState]):
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
        log.info("** PREPARE: CREATE TABLE DESCRIPTIONS **")
        document_elements = self._document_store.get_elements()

        table_descriptions = {}
        for i, element in enumerate(document_elements):
            if isinstance(element, Table):
                table_descriptions[element.id] = await self._get_table_description(document_elements, i, 1000)
                log.info(
                    "Table description for '%s': %s",
                    element.id,
                    table_descriptions[element.id]
                )
            elif isinstance(element, TableChunk):
                raise NotImplemented("TableChunks are not supported yet, please implement here!")

        state.content.table_descriptions = table_descriptions
        return state

    @typechecked()
    async def _get_table_description(
            self,
            document: list[Element],
            index: int,
            text_length: int
    ) -> str:
        elements_before, table, elements_after = get_surrounding_document_elements(
            document,
            index,
            text_length,
        )
        assert isinstance(table, Table)

        html_table = table.metadata.text_as_html
        df = pd.read_html(io.StringIO(html_table))
        assert len(df) == 1
        df = df[0]
        markdown_table = df.to_markdown()

        text_before = "\n".join([e.text for e in elements_before])
        text_after = "\n".join([e.text for e in elements_after])
        agent_executor = create_pandas_dataframe_agent(
            self._llm,
            df,
            agent_type="tool-calling",
            verbose=True,
            allow_dangerous_code=True,
        )
        response = await agent_executor.ainvoke({
            "input": load_prompt("prepare", "find_table_description").render({
                "text_before": text_before,
                "text_after": text_after,
            }),
        })

        description = response["output"]
        if len(description) * 2 >= len(markdown_table):
            description += "\n" + markdown_table
        return description
