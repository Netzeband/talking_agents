from typeguard import typechecked
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import logging
from pydantic import BaseModel, Field

from talking_agents.graph.common.prompt import load_prompt
from talking_agents.graph import INode
from talking_agents.graph.guest import GuestState

log = logging.getLogger(__name__)


class CasualQuestionAnsweringNodeOutput(BaseModel):
    answer: str = Field(..., description="The answer to give to the moderator.")
    is_finished: bool = Field(..., description="Indicates, if the guest wants to end the interview.")


class CasualQuestionAnsweringNode(INode[GuestState]):
    @typechecked()
    def __init__(
            self,
            llm: BaseChatModel,
            tools: list[BaseTool],
    ):
        self._llm = llm
        self._tools = tools

    @typechecked()
    async def run(self, state: GuestState) -> GuestState:
        log.info("** GUEST: CASUAL QUESTION ANSWERING **")
        prompt = ChatPromptTemplate.from_messages([
            ("system", "{system_prompt}"),
            MessagesPlaceholder("history"),
        ])
        model = prompt | self._llm.bind_tools(self._tools)
        should_be_finished = state.is_moderator_finished or state.next_question >= len(state.preparation.questions)
        response: AIMessage = await model.ainvoke({
            "system_prompt": load_prompt("guest", "casual_question_answering").render({
                "role_description": state.setup.guest.get_role_description(),
                "role_information": state.setup.guest.get_private_additional_information(),
                "moderator_name": state.setup.moderator.name,
                "moderator_finished": should_be_finished,
            }),
            "history": state.history + state.messages,
        })

        state.messages.append(response)
        if len(response.tool_calls) > 0:
            log.info(" * Request tools:")
            for tool_call in response.tool_calls:
                log.info("   * %s(%s)", tool_call["name"], tool_call["args"])

        else:
            log.info(" * Final answer: %s", response.content)
            state.answer = response.content
            state.is_finished = should_be_finished

        return state
