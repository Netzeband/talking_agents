import json
from json import JSONDecodeError
from pathlib import PurePosixPath

from typeguard import typechecked
import logging

from talking_agents.graph import INode
from talking_agents.graph.common.prompt import load_prompt
from talking_agents.graph.post_processing import PostProcessingState
from talking_agents.graph.common.interview_content import InterviewRoles

log = logging.getLogger(__name__)


class RenderMarkdownNode(INode[PostProcessingState]):
    @typechecked()
    def __init__(self, min_accepted_groundedness_score: float):
        self._min_accepted_groundedness_score = min_accepted_groundedness_score

    @typechecked()
    async def run(self, state: PostProcessingState) -> PostProcessingState:
        log.info("** POST-PROCESSING: RENDER MARKDOWN **")
        file_name = f"episode_{state.setup.episode_number}_{state.content.language.value}.md"
        markdown_path = state.content.output_path / file_name
        full_markdown_path = state.setup.episode_output_dir / markdown_path
        full_markdown_path.parent.mkdir(exist_ok=True, parents=True)
        with full_markdown_path.open("w", encoding="utf-8") as f:
            f.write(self._get_markdown_text(state))
            state.content.markdown_path = markdown_path
        return state

    @typechecked()
    def _get_interview_text(self, state: PostProcessingState) -> str:
        statements = []
        for message in state.content.interview:
            if message.role == InterviewRoles.MODERATOR:
                text = message.text.split("\n\n")
                text = "_\n\n_".join([t.strip() for t in text])
                statements.append(f"_**{state.setup.moderator.name}:** {text}_")
            elif message.role == InterviewRoles.GUEST:
                statements.append(f"**{state.setup.guest.name}:** {message.text}")
            else:
                raise ValueError(f"Unknown role: {message.role}")
        return "\n\n".join(statements)

    @typechecked()
    def _get_markdown_text(self, state: PostProcessingState) -> str:
        avg_redundancy_score, max_redundancy_score = self._get_redundancy_score(state)
        avg_groundedness_score, min_groundedness_score = self._get_groundedness_score(state)
        return load_prompt("post_processing", f"markdown_{state.content.language.value}").render({
            "episode_number": state.setup.episode_number,
            "date": state.setup.date.strftime("%A the %B %d, %Y"),
            "teaser": state.content.core_teaser,
            "interview": self._get_interview_text(state),
            "average_redundancy_score": f"{avg_redundancy_score * 100:.0f}%",
            "average_groundedness_score": f"{avg_groundedness_score * 100:.0f}%",
            "max_redundancy_score": f"{max_redundancy_score * 100:.0f}%",
            "min_groundedness_score": f"{min_groundedness_score * 100:.0f}%",
            "min_accepted_groundedness_score": f"{self._min_accepted_groundedness_score * 100:.0f}%",
            "paper_title": state.preparation.title,
            "paper_url": state.setup.paper_url,
            "web_sources": self._get_web_sources(state),
        })

    @typechecked()
    def _get_redundancy_score(self, state: PostProcessingState) -> (float, float):
        numbers = []
        for message in state.interview.talk:
            if (message.metadata is not None and
                "redundancy" in message.metadata and
                message.metadata["redundancy"] is not None and
                "redundancy_score" in message.metadata["redundancy"]
            ):
                numbers.append(message.metadata["redundancy"]["redundancy_score"])
        if len(numbers) == 0:
            return 0.0, 0.0
        return sum(numbers)/len(numbers), max(numbers)

    @typechecked()
    def _get_groundedness_score(self, state: PostProcessingState) -> (float, float):
        numbers = []
        for message in state.interview.talk:
            if (message.metadata is not None and
                "groundedness" in message.metadata and
                message.metadata["groundedness"] is not None and
                "grounded_score" in message.metadata["groundedness"]
            ):
                numbers.append(message.metadata["groundedness"]["grounded_score"])
        if len(numbers) == 0:
            return 0.0, 0.0
        return sum(numbers)/len(numbers), min(numbers)

    @typechecked()
    def _get_web_sources(self, state: PostProcessingState) -> str:
        web_sources = []
        for message in state.interview.talk:
            if (message.metadata is not None and
                "sources" in message.metadata and
                message.metadata["sources"] is not None
            ):
                for source in message.metadata["sources"]:
                    try:
                        source_data = json.loads(source)
                        for entry in source_data:
                            web_sources.append(entry["url"])
                    except JSONDecodeError:
                        pass

        web_sources = set(web_sources)
        return "\n".join([f" * [{url}]({url})" for url in web_sources])
