from typeguard import typechecked
import logging
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

from src.talking_agents.graph import INode
from src.talking_agents.graph.common.prompt import load_prompt
from src.talking_agents.common.few_shot_examples import FewShotExamples
from src.talking_agents.graph.common.preparation_content import Question
from src.talking_agents.graph.prepare_question import PrepareQuestionState
from src.talking_agents.graph.prepare_question.get_question_history import get_question_history

log = logging.getLogger(__name__)


class AdaptQuestionNodeOutput(BaseModel):
    adapted_question: str | None = Field(..., description="The new questions, which might prevent the issue.")
    skip: bool = Field(..., description="Indicates, if the question should be skipped completely.")


class AdaptQuestionsNode(INode[PrepareQuestionState]):
    @typechecked()
    def __init__(
            self,
            llm: BaseChatModel,
            question_to_avoid_examples: FewShotExamples,
            min_accepted_grounded_score: float,
            max_accepted_redundancy_score: float,
            max_question_retries: int,
    ):
        self._llm = llm
        self._question_to_avoid_examples = question_to_avoid_examples
        self._min_accepted_grounded_score = min_accepted_grounded_score
        self._max_accepted_redundancy_score = max_accepted_redundancy_score
        self._max_question_retries = max_question_retries

    @typechecked()
    async def run(self, state: PrepareQuestionState) -> PrepareQuestionState:
        log.info("** PREPARE QUESTION: ADAPT QUESTION **")

        state.number_of_retries += 1
        if state.number_of_retries > self._max_question_retries:
            skipped_question = state.current_questions.pop()
            state.skip_and_continue = True
            log.warning(
                f" * Reached maximum number of retries (%s). Skip question '%s'",
                str(self._max_question_retries),
                skipped_question.question,
            )
            return state

        prompt = ChatPromptTemplate.from_messages([
            ("system", "{system_prompt}"),
            MessagesPlaceholder("history"),
        ])
        model = prompt | self._llm.with_structured_output(AdaptQuestionNodeOutput)
        result: AdaptQuestionNodeOutput = await model.ainvoke({
            "system_prompt": load_prompt("prepare_question", "adapt_question").render({
                "role_description": state.setup.moderator.get_role_description(),
                "paper_title": state.preparation.title,
                "topic": state.topic,
                "expectations": state.answer_expectations,
                "old_question": state.current_questions[-1].question,
                "problem_description": self._get_problem_description(state.current_questions[-1]),
                "avoid_question_examples": "\n".join(
                    [f"  * '{example['question']}', better alternative: '{example['alternative']}'" for
                     example in self._question_to_avoid_examples.get_selector()
                                    .select_examples({"question": state.topic})
                     ]
                )
            }),
            "history": get_question_history(
                previous_questions=state.previous_questions,
                current_questions=state.current_questions,
                ModeratorMessageType=AIMessage,
                GuestMessageType=HumanMessage,
            ),
        })

        if result.adapted_question and not result.skip:
            log.info(f" * Adapted question: '{result.adapted_question}'")
            state.current_questions[-1] = Question(
                question=result.adapted_question,
                topic=state.topic,
            )
            state.skip_and_continue = False

        else:
            skipped_question = state.current_questions.pop()
            log.info(f" * Skip question: '{skipped_question.question}'")
            state.skip_and_continue = True

        return state

    @typechecked()
    def _get_problem_description(self, question: Question) -> str:
        if question.follow_up.is_necessary:
            return (f"The answer to the partial question '{question.follow_up.question}' could not be found inside "
                    f"the paper and all tries to get an answer to that failed. So please adapt the question to not "
                    f"contain this aspect/part of the question or skip the question completely, if an adaption is "
                    f"not possible or meaningful.")

        if question.groundedness.score is not None:
            if question.groundedness.score < self._min_accepted_grounded_score:
                return ("The answer to the original question could not really be found inside the paper. "
                        "Please adapt the question to focus more on the paper. A good way to do this is to follow-up "
                        "on an aspect of a previous answer, which is connected with the topic. If this is not possible "
                        "just skip the question completely.")

        if question.redundancy.score is not None:
            if question.redundancy.score > self._max_accepted_redundancy_score:
                return ("The answer to the original question is already covered by answers of previous questions. "
                        "This leads to a very high redundancy in the podcast episode. Please adapt the question to "
                        "focus on a different aspect of the paper or skip it completely to avoid redundancy.")

        log.warning(
            "Could not find reason why to adapt the question. Groundedness-score: %s; Redundancy-score: %s",
            str(question.groundedness.score),
            str(question.redundancy.score)
        )
        return "There was an unknown issue with the answer of the question. Please just skip it!"
