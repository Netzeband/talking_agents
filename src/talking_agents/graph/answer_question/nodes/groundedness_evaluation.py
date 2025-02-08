from typeguard import typechecked
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
import logging

from src.talking_agents.graph.common.prompt import load_prompt
from src.talking_agents.graph import INode
from src.talking_agents.graph.answer_question import AnswerQuestionState

log = logging.getLogger(__name__)


class GroundednessEvaluationOutput(BaseModel):
    # noinspection PyDataclass
    information_from_source: list[str] = Field(
        default_factory=list,
        description="Information in the statement, which is based on the source."
    )
    # noinspection PyDataclass
    information_not_in_source: list[str] = Field(
        default_factory=list,
        description="Information in the statement, which is not based on the source."
    )


class GroundednessEvaluation(INode[AnswerQuestionState]):
    @typechecked()
    def __init__(self, llm: BaseChatModel):
        self._llm = llm

    @typechecked()
    async def run(self, state: AnswerQuestionState) -> AnswerQuestionState:
        log.info("** ANSWER QUESTION: GROUNDEDNESS EVALUATION **")
        prompt = ChatPromptTemplate.from_messages([
            ("system", "{system_prompt}"),
        ])
        model = prompt | self._llm.with_structured_output(GroundednessEvaluationOutput)
        response: GroundednessEvaluationOutput = await model.ainvoke({
            "system_prompt": load_prompt("answer_question", "groundedness_evaluation").render({
                "sources": self._format_sources(state.sources),
                "statement": state.intermediate_answer,
            }),
        })

        grounded_score = self._calculate_grounded_score(response)
        log.info(" * Grounded score: %.2f", grounded_score)
        state.groundedness.grounded_information = response.information_from_source
        state.groundedness.ungrounded_information = response.information_not_in_source
        state.groundedness.score = self._calculate_grounded_score(response)
        state.answers = response.information_from_source + response.information_not_in_source

        return state

    @staticmethod
    @typechecked()
    def _format_sources(sources: list[str] | None) -> str:
        if sources is None:
            return "No source provided."

        return "\n".join([f" * {s}" for s in sources])

    @staticmethod
    @typechecked()
    def _calculate_grounded_score(output: GroundednessEvaluationOutput) -> float:
        total_information = output.information_from_source + output.information_not_in_source
        if len(total_information) == 0:
            return 0.0
        return len(output.information_from_source) / len(total_information)
