from langgraph.graph import StateGraph, START, END
from typeguard import typechecked
import logging

from src.talking_agents.graph.prepare.nodes import Nodes
from src.talking_agents.graph.prepare_question import PrepareQuestionState
from src.talking_agents.graph.prepare_question.nodes import PrepareQuestionNodes
from src.talking_agents.graph import INode

log = logging.getLogger(__name__)


class PrepareQuestionGraph(INode[PrepareQuestionState]):
    @typechecked()
    def __init__(
            self,
            generate_question_node: INode[PrepareQuestionState],
            answer_question_node: INode[PrepareQuestionState],
            adapt_question_node: INode[PrepareQuestionState],
            generate_follow_up_question_node: INode[PrepareQuestionState],
            min_accepted_grounded_score: float,
            max_accepted_redundancy_score: float,
    ):
        self._min_accepted_grounded_score = min_accepted_grounded_score
        self._max_accepted_redundancy_score = max_accepted_redundancy_score

        graph_builder = StateGraph(PrepareQuestionState)
        graph_builder.add_node(PrepareQuestionNodes.GENERATE_QUESTION, generate_question_node.run)
        graph_builder.add_node(PrepareQuestionNodes.ANSWER_QUESTION, answer_question_node.run)
        graph_builder.add_node(PrepareQuestionNodes.ADAPT_QUESTION, adapt_question_node.run)
        graph_builder.add_node(PrepareQuestionNodes.GENERATE_FOLLOW_UP_QUESTION, generate_follow_up_question_node.run)

        graph_builder.add_edge(START, PrepareQuestionNodes.GENERATE_QUESTION)
        graph_builder.add_edge(PrepareQuestionNodes.GENERATE_QUESTION, PrepareQuestionNodes.ANSWER_QUESTION)
        graph_builder.add_conditional_edges(
            PrepareQuestionNodes.ANSWER_QUESTION,
            self._adapt_question_or_follow_up_question
        )
        graph_builder.add_conditional_edges(
            PrepareQuestionNodes.ADAPT_QUESTION,
            self._answer_question_or_end
        )
        graph_builder.add_conditional_edges(
            PrepareQuestionNodes.GENERATE_FOLLOW_UP_QUESTION,
            self._answer_question_or_end
        )

        self._graph = graph_builder.compile()

    @typechecked()
    async def run(self, state: PrepareQuestionState) -> PrepareQuestionState:
        log.info("Start prepare question agent graph.")
        result = PrepareQuestionState.model_validate(await self._graph.ainvoke(
            state,
            {"recursion_limit": 50},
        ))
        return result

    @typechecked()
    def _adapt_question_or_follow_up_question(self, state: PrepareQuestionState) -> PrepareQuestionNodes | str:
        assert state.current_questions[-1].groundedness.score is not None
        assert state.current_questions[-1].redundancy.score is not None

        if state.current_questions[-1].follow_up.is_necessary:
            return PrepareQuestionNodes.ADAPT_QUESTION

        if state.current_questions[-1].groundedness.score < self._min_accepted_grounded_score:
            return PrepareQuestionNodes.ADAPT_QUESTION

        if state.current_questions[-1].redundancy.score > self._max_accepted_redundancy_score:
            return PrepareQuestionNodes.ADAPT_QUESTION

        return PrepareQuestionNodes.GENERATE_FOLLOW_UP_QUESTION

    @typechecked()
    def _answer_question_or_end(self, state: PrepareQuestionState) -> PrepareQuestionNodes | str:
        if not state.skip_and_continue and len(state.current_questions) > 0 and state.current_questions[-1].question:
            return PrepareQuestionNodes.ANSWER_QUESTION

        return END