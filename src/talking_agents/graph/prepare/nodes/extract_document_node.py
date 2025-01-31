import json
from typeguard import typechecked
import logging
from unstructured_client import UnstructuredClient
from typing import Any
from unstructured_client.models import operations, shared
from pathlib import Path

from talking_agents.graph import INode
from talking_agents.graph.prepare import PrepareState
from talking_agents.common.document_store import DocumentStore

log = logging.getLogger(__name__)


class ExtractDocumentNode(INode[PrepareState]):
    @typechecked()
    def __init__(
            self,
            unstructured_client: UnstructuredClient,
            document_store: DocumentStore,
    ):
        self._client = unstructured_client
        self._document_store = document_store

    @typechecked()
    async def run(self, state: PrepareState) -> PrepareState:
        log.info("** PREPARE: EXTRACT DOCUMENT **")

        if state.content.extracted_document_file is not None and state.content.extracted_document_file.exists():
            log.info(f" * Load element cache file: {state.content.extracted_document_file}")
            self._document_store.load_from_file(state.content.extracted_document_file)

        else:
            log.info(f" * Extract elements from file: {state.content.input_file}")
            elements, cache_file = await self._extract_elements(state, state.content.input_file)
            self._document_store.load_from_dict(elements)
            state.content.extracted_document_file = cache_file

        assert self._document_store.is_loaded
        log.info(f" * Document contains {len(self._document_store.get_elements())} elements")
        return state


    @typechecked()
    async def _extract_elements(self, state: PrepareState, file: Path) -> tuple[list[dict[str, Any]], Path]:
        with file.open("rb") as f:
            input_data = f.read()

        request = operations.PartitionRequest(
            partition_parameters=shared.PartitionParameters(
                files=shared.Files(
                    content=input_data,
                    file_name=file.name,
                ),
                strategy=shared.Strategy.HI_RES,
                extract_image_block_types=["Image", "Table"],
                languages=['eng'],
            ),
        )
        result = await self._client.general.partition_async(request=request)

        cache_file = state.setup.episode_output_dir / "extracted_document.json"
        with cache_file.open("w") as f:
            json.dump(result.elements, f, indent=4)

        return result.elements, cache_file
