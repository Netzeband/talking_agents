from typeguard import typechecked
import logging
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

from talking_agents.graph import INode
from talking_agents.graph.common.prompt import load_prompt
from talking_agents.common.few_shot_examples import FewShotExamples
from talking_agents.graph.common.preparation_content import Question
from talking_agents.graph.prepare_question import PrepareQuestionState
from talking_agents.graph.prepare_question.get_question_history import get_question_history

log = logging.getLogger(__name__)


class GenerateFollowUpQuestionNodeOutput(BaseModel):
    follow_up_question: str | None = Field(..., description="The follow-up question to ask.")
    skip: bool = Field(
        ...,
        description="Indicates, if the the topic is already discussed fully and we should continue with a new topic."
    )


class GenerateFollowUpQuestionsNode(INode[PrepareQuestionState]):
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
        log.info("** PREPARE QUESTION: GENERATE FOLLOW-UP QUESTION **")

        prompt = ChatPromptTemplate.from_messages([
            ("system", "{system_prompt}"),
            MessagesPlaceholder("history"),
        ])
        model = prompt | self._llm.with_structured_output(GenerateFollowUpQuestionNodeOutput)
        result: GenerateFollowUpQuestionNodeOutput = await model.ainvoke({
            "system_prompt": load_prompt("prepare_question", "generate_follow_up_question").render({
                "role_description": state.setup.moderator.get_role_description(),
                "paper_title": state.preparation.title,
                "topic": state.topic,
                "upcoming_topics": "\n".join([f" * {t}" for t in state.preparation.topics]),
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

        if result.follow_up_question and not result.skip:
            log.info(f" * New follow-up question: '{result.follow_up_question}'")
            state.current_questions.append(Question(
                question=result.follow_up_question,
                topic=state.topic,
            ))
            state.skip_and_continue = False

        else:
            log.info(f" * Do not ask a follow-up question")
            state.skip_and_continue = True

        return state
