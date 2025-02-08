from typeguard import typechecked
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
import logging

from src.talking_agents.graph.common.prompt import load_prompt
from src.talking_agents.graph import INode
from src.talking_agents.graph.answer_question import AnswerQuestionState
from src.talking_agents.graph.common.preparation_content import Redundancy, Question

log = logging.getLogger(__name__)


class RedundancyEvaluationNodeOutput(BaseModel):
    # noinspection PyDataclass
    new_information: list[str] = Field(
        default_factory=list,
        description="Information with is not covered yet by the conversation history."
    )
    # noinspection PyDataclass
    redundant_information: list[str] = Field(
        default_factory=list,
        description="Information which is already covered by the conversation history."
    )


class RedundancyEvaluationNode(INode[AnswerQuestionState]):
    @typechecked()
    def __init__(self, llm: BaseChatModel):
        self._llm = llm

    @typechecked()
    async def run(self, state: AnswerQuestionState) -> AnswerQuestionState:
        log.info("** ANSWER QUESTION: REDUNDANCY EVALUATION **")
        if not state.answers:
            raise ValueError("Answer are missing.")

        prompt = ChatPromptTemplate.from_messages([
            ("system", "{system_prompt}"),
        ])
        model = prompt | self._llm.with_structured_output(RedundancyEvaluationNodeOutput)
        response: RedundancyEvaluationNodeOutput = await model.ainvoke({
            "system_prompt": load_prompt("answer_question", "redundancy_evaluation").render({
                "history": self._get_conversation_history_string(state.previous_questions),
                "statement": "\n".join([f" * {a}" for a in state.answers]),
            }),
        })

        redundancy_score = self._calculate_redundancy_score(response.new_information, response.redundant_information)
        log.info(" * Redundancy score: %.2f", redundancy_score)
        state.redundancy = Redundancy(
            new_information=response.new_information,
            old_information=response.redundant_information,
            score=redundancy_score,
        )
        return state

    @typechecked()
    def _calculate_redundancy_score(self, new: list[str], redundant: list[str]) -> float:
        new_text = "\n".join(new)
        redundant_text = "\n".join(redundant)
        if len(new_text) + len(redundant_text) == 0:
            return 0.0
        return len(redundant_text) / (len(new_text) + len(redundant_text))

    @typechecked()
    def _get_conversation_history_string(self, previous_questions: list[Question]) -> str:
        history = ""
        for question in previous_questions:
            history += "\nQuestion: " + question.question + "\n\n"
            if question.answer:
                history += "\n".join(f" * {a}" for a in question.answer)
                history += "\n---\n"
        return history
