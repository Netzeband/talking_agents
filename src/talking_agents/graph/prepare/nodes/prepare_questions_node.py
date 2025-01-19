from typeguard import typechecked
import logging

from talking_agents.graph import INode
from talking_agents.graph.common.preparation_content import Question
from talking_agents.graph.prepare.prepare_state import PrepareState
from talking_agents.graph.prepare_question import PrepareQuestionState

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

        for i, topic in enumerate(state.content.topics):
            log.info(f" * Prepare question for topic '{topic}'")
            new_questions = await self._prepare_question_for_topic(state, i, topic, state.content.questions)
            if len(new_questions) > 0:
                state.content.questions.extend(new_questions)
                state.content.store(
                    output_path=state.setup.output_path,
                    episode_number=state.setup.episode_number,
                )
            else:
                log.info(f" * Skip topic '{topic}', because no questions where found.")

        log.info(f"Prepared {len(state.content.questions)} for {len(state.content.topics)}.")
        return state

    async def _prepare_question_for_topic(
            self,
            state: PrepareState,
            topic_index: int,
            topic: str,
            previous_questions: list[Question]
    ) -> list[Question]:
        log.info(f"*** TOPIC {topic_index + 1}/{len(state.content.topics)}: {topic} ***")
        if state.content.next_topic_index > topic_index:
            log.info(" * Skip topic, because questions have already been generated.")
            return []

        result = PrepareQuestionState.model_validate(await self._prepare_question_graph.run(
            PrepareQuestionState(
                setup=state.setup,
                preparation=state.content,
                topic=topic,
                previous_questions=previous_questions,
            )
        ))

        state.content.next_topic_index = topic_index + 1
        return result.current_questions
