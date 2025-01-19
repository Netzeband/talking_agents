from typeguard import typechecked
from typing import Any
from pathlib import Path
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
import yaml
import logging

log = logging.getLogger(__name__)


class FewShotExamples:
    @typechecked()
    def __init__(self, few_shot_example_path: Path, name: str, k: int = 1):
        self._file_path = few_shot_example_path / f"{name}.yaml"
        self._selector: SemanticSimilarityExampleSelector | None = None
        self._k = k

    @typechecked()
    def get_selector(self) -> SemanticSimilarityExampleSelector:
        if self._selector is None:
            log.info("Initialize few-shot examples from '%s'.", self._file_path.name)
            self._selector = SemanticSimilarityExampleSelector.from_examples(
                self._get_few_shot_examples(),
                OpenAIEmbeddings(),
                FAISS,
                k=self._k,
            )
        return self._selector

    @typechecked()
    def _get_few_shot_examples(self) -> list[dict[Any, Any]]:
        with self._file_path.open("r") as f:
            return yaml.safe_load(f)
