from langgraph.graph import StateGraph, START, END
from typeguard import typechecked
from pathlib import Path
import logging

from talking_agents.graph.post_processing.nodes import Nodes
from talking_agents.graph.post_processing import PostProcessingState
from talking_agents.graph import INode

log = logging.getLogger(__name__)


class PostProcessingGraph(INode[PostProcessingState]):
    @typechecked()
    def __init__(
            self,
            create_translation_node: INode[PostProcessingState],
            create_teaser_node: INode[PostProcessingState],
            render_markdown_node: INode[PostProcessingState],
            adapt_interview_node: INode[PostProcessingState],
            create_audio_node: INode[PostProcessingState],
            create_video_node: INode[PostProcessingState],
    ):
        graph_builder = StateGraph(PostProcessingState)
        graph_builder.add_node(Nodes.CREATE_TRANSLATION, create_translation_node.run)
        graph_builder.add_node(Nodes.CREATE_TEASER, create_teaser_node.run)
        graph_builder.add_node(Nodes.RENDER_MARKDOWN, render_markdown_node.run)
        graph_builder.add_node(Nodes.ADAPT_INTERVIEW, adapt_interview_node.run)
        graph_builder.add_node(Nodes.CREATE_AUDIO, create_audio_node.run)
        graph_builder.add_node(Nodes.CREATE_VIDEO, create_video_node.run)

        graph_builder.add_conditional_edges(START, self._transition)
        graph_builder.add_conditional_edges(Nodes.CREATE_TRANSLATION, self._transition)
        graph_builder.add_conditional_edges(Nodes.CREATE_TEASER, self._transition)
        graph_builder.add_conditional_edges(Nodes.RENDER_MARKDOWN, self._transition)
        graph_builder.add_conditional_edges(Nodes.ADAPT_INTERVIEW, self._transition)
        graph_builder.add_conditional_edges(Nodes.CREATE_AUDIO, self._transition)
        graph_builder.add_conditional_edges(Nodes.CREATE_VIDEO, self._transition)

        self._graph = graph_builder.compile()

    @typechecked()
    async def run(self, state: PostProcessingState) -> PostProcessingState:
        log.info("Start post-processing agent graph.")
        result = PostProcessingState.model_validate(await self._graph.ainvoke(state))
        return result

    @typechecked()
    def _transition(self, state: PostProcessingState) -> Nodes | str:
        state.content.store(
            output_path=state.setup.output_path,
            episode_number=state.setup.episode_number,
        )

        if state.content.interview is None:
            log.info(" => Create translation of interview ...")
            return Nodes.CREATE_TRANSLATION

        if state.content.full_teaser is None or state.content.core_teaser is None:
            log.info(" => Create teaser description ...")
            return Nodes.CREATE_TEASER

        if (state.content.markdown_path is None or
            not (state.setup.episode_output_dir / Path(state.content.markdown_path)).exists() or
            state.content.teaser_markdown_path is None or
            not (state.setup.episode_output_dir / Path(state.content.teaser_markdown_path)).exists()
        ):
            log.info(" => Render Markdown file ...")
            return Nodes.RENDER_MARKDOWN

        if state.content.audio_adapted_interview is None:
            log.info(" => Create audio adaption of the interview ...")
            return Nodes.ADAPT_INTERVIEW

        if (state.content.audio_path is None or
                not (state.setup.episode_output_dir / Path(state.content.audio_path)).exists()
        ):
            log.info(" => Create audio file ...")
            return Nodes.CREATE_AUDIO

        if (state.content.video is None) or not (state.content.video.exists()):
            log.info(" => Create video file ...")
            return Nodes.CREATE_VIDEO

        return END
