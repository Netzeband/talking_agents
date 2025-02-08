from typeguard import typechecked
from langchain_core.language_models import BaseChatModel
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, SystemMessage
from pydantic import BaseModel, Field
import logging

from src.talking_agents.graph.common.prompt import load_prompt
from src.talking_agents.graph import INode
from src.talking_agents.graph.interview.interview_state import InterviewState
from src.talking_agents.graph.common.interview_content import Message, InterviewRoles

log = logging.getLogger(__name__)


class ModeratorNodeOutput(BaseModel):
    question: str = Field(..., description="The question or statement from the moderator.")


class ModeratorNode(INode[InterviewState]):
    @typechecked()
    def __init__(self, llm: BaseChatModel):
        self._llm = llm

    @typechecked()
    async def run(self, state: InterviewState) -> InterviewState:
        log.info("** INTERVIEW: MODERATOR **")

        prompt = ChatPromptTemplate([
            ("system", "{system_prompt}"),
            MessagesPlaceholder("history"),
        ])
        model = prompt | self._llm.with_structured_output(ModeratorNodeOutput)
        response = await model.ainvoke({
            "system_prompt": load_prompt("interview", "moderator").render({
                "role_description": state.setup.moderator.get_role_description(),
                "guest_name": state.setup.guest.name,
            }),
            "history": self._create_history(state.content.talk) + self._get_ai_assistant_message(state)
        })

        log.info("Moderator: %s", response.question)
        state.content.talk.append(Message(
            role=InterviewRoles.MODERATOR,
            text=response.question,
        ))
        state.content.moderator_is_finished = state.content.next_question > len(state.preparation.questions)
        return state

    @typechecked()
    def _get_ai_assistant_message(self, state: InterviewState) -> list[BaseMessage]:
        return [SystemMessage(
            content=load_prompt("interview", "ai_assistant_message").render({
                "information": self._get_prepared_content(state),
            })
        )]

    @typechecked()
    def _get_prepared_content(self, state: InterviewState) -> str:
        if state.content.next_question == -1:
            return ("The first statement is the introduction of the podcast, the topic and the guest. You already "
                    f"prepared the following text:\n{state.preparation.introduction}\n\n")

        elif state.content.next_question < len(state.preparation.questions):
            additional_info = ""
            if state.content.next_question == len(state.preparation.questions) - 1:
                additional_info = "This is the last question."
            question = state.preparation.questions[state.content.next_question].question
            return (f"{question}\n\n"
                    "Please find a good transition from the last answer of your guest. For that you can also rephrase "
                    f"your question without changing its content. {additional_info}")

        elif state.content.next_question == len(state.preparation.questions):
            return (f"All prepared questions are asked. Please ask your guest for a summary, final words or last "
                    "though on that topic, before you wrap-up the episode.")

        else:
            return f"You prepared a wrap-up text for the episode:\n{state.preparation.wrapup}"

    @typechecked()
    def _create_history(self, talk: list[Message]) -> list[BaseMessage]:
        history = []
        for message in talk:
            if message.role == InterviewRoles.MODERATOR:
                history.append(AIMessage(content=message.text))
            else:
                history.append(HumanMessage(content=message.text))
        return history
