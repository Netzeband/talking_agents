from typeguard import typechecked
import logging

from src.talking_agents.graph import INode
from src.talking_agents.graph.common.preparation_content import Question
from src.talking_agents.graph.prepare.prepare_state import PrepareState
from src.talking_agents.graph.prepare_question import PrepareQuestionState
from src.talking_agents.graph.common import get_max_state_from_number, is_max_state

log = logging.getLogger(__name__)


class PrepareQuestionsNode(INode[PrepareState]):
    @typechecked()
    def __init__(
            self,
            prepare_question_graph: INode[PrepareQuestionState]
    ):
        self._prepare_question_graph = prepare_question_graph

    @typechecked()
    async def run(self, state: PrepareState) -> PrepareState:
        log.info("** PREPARE: PREPARE QUESTIONS **")

        if not state.content.questions:
            state.content.questions = []

        max_topic_index = get_max_state_from_number(
            ["prepare", "prepare_questions"],
            state.setup.max_state, 2, 0, len(state.content.topics)
        )

        for i, topic in enumerate(state.content.topics):
            if is_max_state(max_topic_index, i):
                state.end_graph = True
                break

            new_questions = await self._prepare_question_for_topic(
                state,
                i,
                topic.description,
                topic.answer_expectation,
                state.content.questions
            )
            if len(new_questions) > 0:
                state.content.questions.extend(new_questions)

            else:
                log.info(f" * Skip topic '{topic.description}', because no questions where found.")
                if topic.description not in set([q.topic for q in state.content.questions]):
                    state.content.skipped_topics.append(topic.description)

            state.content.store(
                output_path=state.setup.output_path,
                episode_number=state.setup.episode_number,
            )

        log.info(f"Prepared {len(state.content.questions)} for {len(state.content.topics)}.")
        return state

    async def _prepare_question_for_topic(
            self,
            state: PrepareState,
            topic_index: int,
            topic: str,
            answer_expectations: str,
            previous_questions: list[Question]
    ) -> list[Question]:
        questions = state.content.questions or []
        topics_already_handles = set([q.topic for q in questions] + state.content.skipped_topics)
        if topic in topics_already_handles:
            log.info(" * Skip topic '%s', because questions have already been generated.", topic)
            return []

        log.info(f"*** TOPIC {topic_index + 1}/{len(state.content.topics)}: {topic} ***")
        result = PrepareQuestionState.model_validate(await self._prepare_question_graph.run(
            PrepareQuestionState(
                setup=state.setup,
                preparation=state.content,
                topic=topic,
                answer_expectations=answer_expectations,
                previous_questions=previous_questions,
                expect_examples=topic_index > 0, # expect examples for all topics except the first one
            )
        ))

        return result.current_questions
