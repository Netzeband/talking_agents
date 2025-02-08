import logging
from pydantic import BaseModel, Field
from typeguard import typechecked
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from src.talking_agents.graph import INode
from src.talking_agents.common.few_shot_examples import FewShotExamples
from src.talking_agents.graph.common.prompt import load_prompt
from src.talking_agents.graph.common.preparation_content import Question
from src.talking_agents.graph.prepare_question import PrepareQuestionState
from src.talking_agents.graph.prepare_question.get_question_history import get_question_history

log = logging.getLogger(__name__)


class GenerateQuestionNodeOutput(BaseModel):
    question: str = Field(
        ...,
        description="The generated question."
    )


class GenerateQuestionNode(INode[PrepareQuestionState]):
    @typechecked()
    def __init__(
            self,
            llm: BaseChatModel,
            question_to_avoid_examples: FewShotExamples,
    ):
        self._llm = llm
        self._question_to_avoid_examples = question_to_avoid_examples

    @typechecked()
    async def run(self, state: PrepareQuestionState) -> PrepareQuestionState:
        log.info("** PREPARE QUESTION: GENERATE NEW QUESTION **")
        prompt = ChatPromptTemplate.from_messages([
            ("system", "{system_prompt}"),
            MessagesPlaceholder("history"),
        ])
        model = prompt | self._llm.with_structured_output(GenerateQuestionNodeOutput)
        result: GenerateQuestionNodeOutput = await model.ainvoke({
            "system_prompt": load_prompt("prepare_question", "generate_question").render({
                "role_description": state.setup.moderator.get_role_description(),
                "paper_title": state.preparation.title,
                "topic": state.topic,
                "expectations": state.answer_expectations,
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
            ) + [SystemMessage(content=f"Generate now a question for the topic:\n{state.topic}")],
        })

        log.info(f" * Generated question: '{result.question}'")
        state.current_questions.append(Question(
            question=result.question,
            topic=state.topic,
        ))
        state.skip_and_continue = False

        return state
