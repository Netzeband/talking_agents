from typeguard import typechecked
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
import logging

from talking_agents.graph.common.prompt import load_prompt
from talking_agents.graph import INode
from talking_agents.graph.answer_question import AnswerQuestionState

log = logging.getLogger(__name__)


class CompletenessEvaluationOutput(BaseModel):
    is_complete: bool | None = Field(
        None,
        description="Indicates if the answer, answers the question completely."
    )
    follow_up_question: str | None = Field(
        None,
        description="In case the answer answers the question not completely, the spect of the question which has not "
                    "been answered can be asked in a follow up question."
    )


class CompletenessEvaluation(INode[AnswerQuestionState]):
    @typechecked()
    def __init__(self, llm: BaseChatModel):
        self._llm = llm

    @typechecked()
    async def run(self, state: AnswerQuestionState) -> AnswerQuestionState:
        log.info("** ANSWER QUESTION: COMPLETENESS EVALUATION **")
        prompt = ChatPromptTemplate.from_messages([
            ("system", "{system_prompt}"),
        ])
        model = prompt | self._llm.with_structured_output(CompletenessEvaluationOutput)
        response: CompletenessEvaluationOutput = await model.ainvoke({
            "system_prompt": load_prompt("answer_question", "completeness_evaluation").render({
                "question": state.original_question,
                "answers": "\n".join([f" * {a}" for a in state.answers]),
            }),
        })

        if response.is_complete:
            log.info(" * Question is fully answered")
            state.follow_up.is_necessary = False
            state.follow_up.question = None

        else:
            if response.follow_up_question is None:
                log.warning("Follow-up question is required but not defined.")
                state.follow_up.question = state.original_question
            else:
                state.follow_up.question = response.follow_up_question
            state.follow_up.is_necessary = True
            state.follow_up.follow_ups += 1
            log.info(" * Follow-Up question: %s", state.follow_up.question)

        return state
