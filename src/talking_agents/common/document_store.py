from typeguard import typechecked
import json
from typing import Any
from pathlib import Path
from unstructured.documents.elements import Element
from unstructured.staging.base import elements_from_dicts


class DocumentStore:
    def __init__(self):
        self._elements: list[Element] | None = None

    @typechecked()
    def load_from_file(self, file: Path):
        with file.open("r") as f:
            self.load_from_dict(json.load(f))

    @typechecked()
    def load_from_dict(self, elements_dicts: list[dict[str, Any]]):
        self._elements = elements_from_dicts(elements_dicts)

    @typechecked()
    def is_ready(self) -> bool:
        return self._elements is not None

    @typechecked()
    def get_elements(self) -> list[Element]:
        assert self.is_ready()
        return self._elements

    @typechecked()
    def set_elements(self, new_elements: list[Element]):
        self._elements = new_elements
