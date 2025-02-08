import sys

from langgraph.graph import StateGraph, START, END
from typeguard import typechecked
import logging

from src.talking_agents.graph.common.preparation_content import Question
from src.talking_agents.graph.prepare.nodes import Nodes
from src.talking_agents.graph.prepare.prepare_state import PrepareState
from src.talking_agents.graph import INode
from src.talking_agents.common.vector_store import VectorStore
from src.talking_agents.common.document_store import DocumentStore
from src.talking_agents.graph.common.preparation_content import Topic
from src.talking_agents.graph.common import is_max_state, get_max_state

log = logging.getLogger(__name__)


class PrepareGraph(INode[PrepareState]):
    @typechecked()
    def __init__(
            self,
            vector_store: VectorStore,
            example_store: VectorStore,
            document_store: DocumentStore,
            download_paper_node: INode[PrepareState],
            extract_document_node: INode[PrepareState],
            create_image_descriptions_node: INode[PrepareState],
            create_table_descriptions_node: INode[PrepareState],
            create_title_node: INode[PrepareState],
            create_summary_node: INode[PrepareState],
            create_vector_store_node: INode[PrepareState],
            find_example_node: INode[PrepareState],
            create_introduction_node: INode[PrepareState],
            create_topics_node: INode[PrepareState],
            prepare_questions_node: INode[PrepareState],
            create_wrapup_node: INode[PrepareState],
    ):
        self._vector_store = vector_store
        self._example_store = example_store
        self._document_store = document_store

        graph_builder = StateGraph(PrepareState)
        graph_builder.add_node(Nodes.DOWNLOAD_PAPER, download_paper_node.run)
        graph_builder.add_node(Nodes.EXTRACT_DOCUMENT, extract_document_node.run)
        graph_builder.add_node(Nodes.CREATE_IMAGE_DESCRIPTIONS, create_image_descriptions_node.run)
        graph_builder.add_node(Nodes.CREATE_TABLE_DESCRIPTIONS, create_table_descriptions_node.run)
        graph_builder.add_node(Nodes.CREATE_VECTOR_STORE, create_vector_store_node.run)
        graph_builder.add_node(Nodes.FIND_EXAMPLES, find_example_node.run)
        graph_builder.add_node(Nodes.CREATE_TITLE, create_title_node.run)
        graph_builder.add_node(Nodes.CREATE_SUMMARY, create_summary_node.run)
        graph_builder.add_node(Nodes.CREATE_INTRODUCTION, create_introduction_node.run)
        graph_builder.add_node(Nodes.CREATE_TOPICS, create_topics_node.run)
        graph_builder.add_node(Nodes.PREPARE_QUESTIONS, prepare_questions_node.run)
        graph_builder.add_node(Nodes.CREATE_WRAP_UP, create_wrapup_node.run)

        graph_builder.add_conditional_edges(START, self._transition)
        graph_builder.add_conditional_edges(Nodes.DOWNLOAD_PAPER, self._transition)
        graph_builder.add_conditional_edges(Nodes.EXTRACT_DOCUMENT, self._transition)
        graph_builder.add_conditional_edges(Nodes.CREATE_IMAGE_DESCRIPTIONS, self._transition)
        graph_builder.add_conditional_edges(Nodes.CREATE_TABLE_DESCRIPTIONS, self._transition)
        graph_builder.add_conditional_edges(Nodes.CREATE_VECTOR_STORE, self._transition)
        graph_builder.add_conditional_edges(Nodes.FIND_EXAMPLES, self._transition)
        graph_builder.add_conditional_edges(Nodes.CREATE_TITLE, self._transition)
        graph_builder.add_conditional_edges(Nodes.CREATE_SUMMARY, self._transition)
        graph_builder.add_conditional_edges(Nodes.CREATE_INTRODUCTION, self._transition)
        graph_builder.add_conditional_edges(Nodes.CREATE_TOPICS, self._transition)
        graph_builder.add_conditional_edges(Nodes.PREPARE_QUESTIONS, self._transition)
        graph_builder.add_conditional_edges(Nodes.CREATE_WRAP_UP, self._transition)

        self._graph = graph_builder.compile()

    @typechecked()
    async def run(self, state: PrepareState) -> PrepareState:
        log.info("Start prepare agent graph.")
        state.max_state = get_max_state(
            ["prepare"], state.setup.max_state, 1, Nodes
        )
        result = PrepareState.model_validate(await self._graph.ainvoke(state))
        return result

    @typechecked()
    def _transition(self, state: PrepareState) -> Nodes | str:
        state.content.store(
            output_path=state.setup.output_path,
            episode_number=state.setup.episode_number,
        )

        if state.end_graph:
            print(f"Abort FSM: Maximum state '{state.max_state}' reached.")
            return END

        if state.content.input_file is None:
            log.info(" => Input file does not exist so far ...")
            return Nodes.DOWNLOAD_PAPER
        elif is_max_state(state.max_state, Nodes.DOWNLOAD_PAPER):
            return END

        if ((state.content.extracted_document_file is None) or
                (not state.content.extracted_document_file.exists()) or
                (not self._document_store.is_ready())
        ):
            log.info(" => Document is not extracted ...")
            return Nodes.EXTRACT_DOCUMENT
        elif is_max_state(state.max_state, Nodes.EXTRACT_DOCUMENT):
            return END

        if state.content.image_descriptions is None:
            log.info(" => Image descriptions not created ...")
            return Nodes.CREATE_IMAGE_DESCRIPTIONS
        elif is_max_state(state.max_state, Nodes.CREATE_IMAGE_DESCRIPTIONS):
            return END

        if state.content.table_descriptions is None:
            log.info(" => Table descriptions not created ...")
            return Nodes.CREATE_TABLE_DESCRIPTIONS
        elif is_max_state(state.max_state, Nodes.CREATE_TABLE_DESCRIPTIONS):
            return END

        if (state.content.vector_store_entries is None or
            not self._vector_store.is_ready() or
            state.content.vector_store_entries != self._vector_store.get_number_of_entries()
        ):
            assert state.content.image_descriptions is not None
            assert state.content.table_descriptions is not None
            log.info(" => Vector store not created ...")
            return Nodes.CREATE_VECTOR_STORE
        elif is_max_state(state.max_state, Nodes.CREATE_VECTOR_STORE):
            return END

        if (state.content.example_store_entries is None or
            not self._example_store.is_ready() or
            state.content.example_store_entries != self._example_store.get_number_of_entries()
        ):
            assert self._vector_store.is_ready()
            log.info(" => Example store not created ...")
            return Nodes.FIND_EXAMPLES
        elif is_max_state(state.max_state, Nodes.FIND_EXAMPLES):
            return END

        if state.content.title is None:
            log.info(" => Title not created ...")
            return Nodes.CREATE_TITLE
        elif is_max_state(state.max_state, Nodes.CREATE_TITLE):
            return END

        if state.content.summary is None:
            log.info(" => Summary not created ...")
            return Nodes.CREATE_SUMMARY
        elif is_max_state(state.max_state, Nodes.CREATE_SUMMARY):
            return END

        if state.content.topics is None:
            log.info(" => Topics not created ...")
            return Nodes.CREATE_TOPICS
        elif is_max_state(state.max_state, Nodes.CREATE_TOPICS):
            return END

        if state.content.introduction is None:
            log.info(" => Introduction not created ...")
            return Nodes.CREATE_INTRODUCTION
        elif is_max_state(state.max_state, Nodes.CREATE_INTRODUCTION):
            return END

        if (state.content.questions is None or
                not self._is_every_topic_already_handled(
                    state.content.topics, state.content.skipped_topics, state.content.questions
                )):
            log.info(" => Questions not created ...")
            return Nodes.PREPARE_QUESTIONS
        elif is_max_state(state.max_state, Nodes.PREPARE_QUESTIONS):
            return END

        if state.content.wrapup is None:
            log.info(" => Wrap-up not created ...")
            return Nodes.CREATE_WRAP_UP
        elif is_max_state(state.max_state, Nodes.CREATE_WRAP_UP):
            return END

        log.info(" => Finished prepare agent graph.")
        return END


    @staticmethod
    @typechecked()
    def _is_every_topic_already_handled(
            topics: list[Topic],
            skipped_topics: list[str],
            questions: list[Question],
    ) -> bool:
        handled_topics = set([q.topic for q in questions] + skipped_topics)
        return all([t.description in handled_topics for t in topics])
