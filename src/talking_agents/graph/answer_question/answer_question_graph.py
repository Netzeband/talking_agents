from langgraph.graph import StateGraph, START, END
from typeguard import typechecked
import logging

from talking_agents.graph.answer_question import AnswerQuestionState
from talking_agents.graph.answer_question.nodes import AnswerQuestionNodes
from talking_agents.graph import INode

log = logging.getLogger(__name__)


class AnswerQuestionGraph(INode[AnswerQuestionState]):
    @typechecked()
    def __init__(
            self,
            question_rephrase_node: INode[AnswerQuestionState],
            question_answering_node: INode[AnswerQuestionState],
            groundedness_evaluation_node: INode[AnswerQuestionState],
            redo_answer_node: INode[AnswerQuestionState],
            completeness_evaluation_node: INode[AnswerQuestionState],
            follow_up_answer_node: INode[AnswerQuestionState],
            redundancy_evaluation_node: INode[AnswerQuestionState],
            min_grounded_score: float,
            max_retries: int,
            max_follow_up_answers: int,
    ):
        self._min_grounded_score = min_grounded_score
        self._max_retries = max_retries
        self._max_follow_up_answers = max_follow_up_answers

        graph_builder = StateGraph(AnswerQuestionState)
        graph_builder.add_node(AnswerQuestionNodes.QUESTION_REPHRASE, question_rephrase_node.run)
        graph_builder.add_node(AnswerQuestionNodes.QUESTION_ANSWERING, question_answering_node.run)
        graph_builder.add_node(AnswerQuestionNodes.GROUNDEDNESS_EVALUATION, groundedness_evaluation_node.run)
        graph_builder.add_node(AnswerQuestionNodes.REDO_ANSWER, redo_answer_node.run)
        graph_builder.add_node(AnswerQuestionNodes.COMPLETENESS_EVALUATION, completeness_evaluation_node.run)
        graph_builder.add_node(AnswerQuestionNodes.FOLLOW_UP_ANSWER, follow_up_answer_node.run)
        graph_builder.add_node(AnswerQuestionNodes.REDUNDANCY_EVALUATION, redundancy_evaluation_node.run)

        graph_builder.add_edge(START, AnswerQuestionNodes.QUESTION_REPHRASE)
        graph_builder.add_edge(AnswerQuestionNodes.QUESTION_REPHRASE, AnswerQuestionNodes.QUESTION_ANSWERING)

        graph_builder.add_edge(AnswerQuestionNodes.QUESTION_ANSWERING, AnswerQuestionNodes.GROUNDEDNESS_EVALUATION)
        graph_builder.add_conditional_edges(
            AnswerQuestionNodes.GROUNDEDNESS_EVALUATION,
            self._redo_answer_or_completeness_evaluation
        )
        graph_builder.add_edge(AnswerQuestionNodes.REDO_ANSWER, AnswerQuestionNodes.GROUNDEDNESS_EVALUATION)

        graph_builder.add_conditional_edges(
            AnswerQuestionNodes.COMPLETENESS_EVALUATION,
            self._follow_up_answer_or_redundancy_evaluation
        )
        graph_builder.add_edge(AnswerQuestionNodes.FOLLOW_UP_ANSWER, AnswerQuestionNodes.GROUNDEDNESS_EVALUATION)

        graph_builder.add_edge(AnswerQuestionNodes.REDUNDANCY_EVALUATION, END)

        self._graph = graph_builder.compile()

    @typechecked()
    async def run(self, state: AnswerQuestionState) -> AnswerQuestionState:
        log.info("Start answer question agent graph.")
        result = AnswerQuestionState.model_validate(await self._graph.ainvoke(state))
        return result


    @typechecked()
    def _redo_answer_or_completeness_evaluation(self, state: AnswerQuestionState) -> AnswerQuestionNodes | str:
        assert state.groundedness.score is not None

        if state.groundedness.score < self._min_grounded_score:
            if state.tries <= self._max_retries:
                return AnswerQuestionNodes.REDO_ANSWER

            else:
                log.warning(
                    f"After {state.tries} the groundedness score is still: {state.groundedness.score*100:.2f}%. "
                    f"Stop retries here!"
                )

        return AnswerQuestionNodes.COMPLETENESS_EVALUATION

    @typechecked()
    def _follow_up_answer_or_redundancy_evaluation(self, state: AnswerQuestionState) -> AnswerQuestionNodes | str:
        if state.follow_up.is_necessary and state.follow_up.follow_ups <= self._max_follow_up_answers:
            return AnswerQuestionNodes.FOLLOW_UP_ANSWER

        return AnswerQuestionNodes.REDUNDANCY_EVALUATION
