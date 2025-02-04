from typeguard import typechecked
import logging

from talking_agents.graph import INode
from talking_agents.graph.common.preparation_content import Question
from talking_agents.graph.prepare_question import PrepareQuestionState
from talking_agents.graph.answer_question import AnswerQuestionState

log = logging.getLogger(__name__)


class AnswerQuestionsNode(INode[PrepareQuestionState]):
    @typechecked()
    def __init__(
            self,
            answer_question_graph: INode[AnswerQuestionState]
    ):
        self._answer_question_graph = answer_question_graph

    @typechecked()
    async def run(self, state: PrepareQuestionState) -> PrepareQuestionState:
        log.info("** PREPARE: ANSWER QUESTIONS **")

        previous_questions = state.previous_questions
        assert len(state.current_questions) >= 1
        if len(state.current_questions) > 1:
            previous_questions.extend(state.current_questions[:-1])

        result: AnswerQuestionState = await self._answer_question_graph.run(AnswerQuestionState(
            setup=state.setup,
            preparation=state.preparation,
            previous_questions=previous_questions,
            answer_expectations=state.answer_expectations,
            original_question=state.current_questions[-1].question,
            expect_examples=state.expect_examples,
        ))

        state.current_questions[-1].metadata["rephrased_question"] = result.rephrased_question
        state.current_questions[-1].metadata["intermediate_answer"] = result.intermediate_answer

        state.current_questions[-1].metadata["sources"] = result.sources

        state.current_questions[-1].answer = result.answers
        state.current_questions[-1].redundancy = result.redundancy
        state.current_questions[-1].groundedness = result.groundedness
        state.current_questions[-1].follow_up = result.follow_up
        return state
