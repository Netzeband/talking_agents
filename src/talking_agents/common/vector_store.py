from langchain_openai import OpenAIEmbeddings
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_core.documents import Document
from langchain_core.tools import BaseTool
from langchain_community.vectorstores import FAISS
from pathlib import Path
from typeguard import typechecked
from langchain_core.tools import RetrieverInput, Tool
from langchain.tools.retriever import create_retriever_tool
import faiss
import json


class VectorStore:
    @typechecked()
    def __init__(
            self,
            embeddings: OpenAIEmbeddings,
            tool_name: str | None = None,
            tool_description: str | None = None,
    ):
        self._embeddings = embeddings
        self._vector_store: FAISS | None = None
        self._retriever_tool: BaseTool | None = None
        self._text_content: dict[str, str] = {}
        self._tool_name = tool_name or "search_paper"
        self._tool_description = (tool_description or
                                  "This tool is used to search and retrieve information from the paper.")

    @typechecked()
    def is_ready(self) -> bool:
        return self._vector_store is not None

    @typechecked()
    def load(self, path: Path):
        self._vector_store = FAISS.load_local(
            str(path / "faiss"),
            self._embeddings,
            allow_dangerous_deserialization=True,
        )
        with open(path / "text_content.json", "r") as f:
            self._text_content = json.load(f)

    @typechecked()
    def create_from_documents(self, chunks: dict[str, Document]):
        self._vector_store = FAISS(
            embedding_function=self._embeddings,
            index=faiss.IndexFlatL2(len(self._embeddings.embed_query("hello world"))),
            docstore=InMemoryDocstore(),
            index_to_docstore_id={},
        )
        self._vector_store.add_documents(
            documents=list([c for c in chunks.values()]),
            ids=list(chunks.keys())
        )
        self._text_content = {k: v.page_content for k, v in chunks.items()}

    @typechecked()
    def save(self, path: Path):
        if not self.is_ready():
            raise Exception(
                "No vector store created now. Either load a vector store or create a new one from documents."
            )
        self._vector_store.save_local(str(path / "faiss"))
        with open(path / "text_content.json", "w") as f:
            json.dump(self._text_content, f, indent=4)

    @typechecked()
    def get_number_of_entries(self) -> int:
        if not self.is_ready():
            raise Exception(
                "No vector store created now. Either load a vector store or create a new one from documents."
            )
        assert self._vector_store.index.ntotal == len(self._text_content)
        return self._vector_store.index.ntotal

    @typechecked()
    def get_text_content(self) -> dict[str, str]:
        return self._text_content

    @typechecked()
    def get_retrieval_tool(self) -> BaseTool:
        return Tool(
            name=self._tool_name,
            description=self._tool_description,
            func=self._retrieve,
            coroutine=self._aretrieve,
            args_schema=RetrieverInput,
        )

    def _get_retrival_tool(self) -> BaseTool:
        if self._retriever_tool is None:
            if not self.is_ready():
                raise Exception(
                    "No vector store created now. Either load a vector store or create a new one from documents."
                )
            self._retriever_tool = create_retriever_tool(
                retriever=self._vector_store.as_retriever(search_kwargs={"k": 10}),
                name="search_paper",
                description="This tool is used to search for and retrieve information from the paper.",
            )
        return self._retriever_tool

    def _retrieve(self, *args, **kwargs):
        tool = self._get_retrival_tool()
        return tool.invoke(*args, **kwargs)

    async def _aretrieve(self, *args, **kwargs):
        tool = self._get_retrival_tool()
        return await tool.ainvoke(*args, **kwargs)
