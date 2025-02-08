from typeguard import typechecked
import logging
import re
import urllib.parse
import httpx
from pathlib import Path

from src.talking_agents.graph import INode
from src.talking_agents.graph.prepare import PrepareState

log = logging.getLogger(__name__)


class DownloadPaperNode(INode[PrepareState]):
    @typechecked()
    async def run(self, state: PrepareState) -> PrepareState:
        log.info("** PREPARE: DOWNLOAD PAPER **")

        if state.setup.document_path is not None:
            state.content.input_file = Path(str(state.setup.document_path))
            log.info(f" * Using local file: {state.content.input_file}")

        else:
            log.info(f" * Download file: {state.setup.paper_url}")
            url = urllib.parse.urlparse(state.setup.paper_url)
            if url.hostname == "arxiv.org":
                state.content.input_file = self._download_arxiv_file(
                    state.setup.paper_url,
                    state.setup.episode_output_dir,
                )
            else:
                state.content.input_file = self._download_file(
                    state.setup.paper_url,
                    state.setup.episode_output_dir,
                )

            log.info(f" * Downloaded file: {state.content.input_file}")

        return state

    @typechecked()
    def _download_file(self, url: str, output_path: Path) -> Path:
        input_file = output_path / "paper.pdf"
        response = httpx.get(url)
        assert response.status_code == httpx.codes.OK
        with input_file.open("wb") as f:
            f.write(response.content)
        return input_file

    ARXIV_PATTERN = re.compile(r"^https://arxiv\.org/([^/]*)/(.*)")
    @typechecked()
    def _download_arxiv_file(self, url: str, output_path: Path) -> Path:
        match = self.ARXIV_PATTERN.match(url)
        assert match is not None
        arxiv_id = match.groups()[1]
        log.info(f" * Detected Arxiv ID: {arxiv_id}")
        url = f"https://arxiv.org/pdf/{arxiv_id}"
        return self._download_file(url, output_path)
