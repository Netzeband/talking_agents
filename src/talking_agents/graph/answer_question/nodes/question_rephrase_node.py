from typeguard import typechecked
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
import logging

from talking_agents.graph.common.prompt import load_prompt
from talking_agents.common.few_shot_examples import FewShotExamples
from talking_agents.graph import INode
from talking_agents.graph.answer_question import AnswerQuestionState
from talking_agents.common import VectorStore

log = logging.getLogger(__name__)


class QuestionRephraseNodeOutput(BaseModel):
    rephrased_question: str = Field(..., description="The rephrased question.")


class QuestionRephraseNode(INode[AnswerQuestionState]):
    @typechecked()
    def __init__(
            self,
            llm: BaseChatModel,
            rephrase_examples: FewShotExamples,
    ):
        self._llm = llm
        self._rephrase_examples = rephrase_examples

    @typechecked()
    async def run(self, state: AnswerQuestionState) -> AnswerQuestionState:
        log.info("** PREPARE: QUESTION REPHRASE **")
        prompt = ChatPromptTemplate.from_messages([
            ("system", "{system_prompt}"),
        ])
        model = prompt | self._llm.with_structured_output(QuestionRephraseNodeOutput)
        response = await model.ainvoke({
            "system_prompt": load_prompt("answer_question", "question_rephrase").render({
                "role_description": state.setup.guest.get_role_description(),
                "moderator_name": state.setup.moderator.name,
                "summary": state.preparation.summary,
                "question": state.original_question,
                "examples": "\n".join(
                    [f" * {example['example']}" for example
                     in self._rephrase_examples.get_selector().select_examples({"question": state.original_question})]
                )
            }),
        })

        log.info(" * Rephrased Question: %s", response.rephrased_question)
        state.rephrased_question = response.rephrased_question
        return state
