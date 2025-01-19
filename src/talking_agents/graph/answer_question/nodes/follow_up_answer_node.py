from typeguard import typechecked
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool
from langchain_core.messages import AIMessage, ToolMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import logging

from talking_agents.graph.common.prompt import load_prompt
from talking_agents.graph import INode
from talking_agents.graph.answer_question import AnswerQuestionState

log = logging.getLogger(__name__)


class FollowUpAnswerNode(INode[AnswerQuestionState]):
    @typechecked()
    def __init__(
            self,
            llm: BaseChatModel,
            tools: list[BaseTool],
    ):
        self._llm = llm
        self._tools = tools

    @typechecked()
    async def run(self, state: AnswerQuestionState) -> AnswerQuestionState:
        log.info("** ANSWER QUESTION: FOLLOW UP ANSWER **")
        assert state.follow_up.question is not None

        # consider only the latest tool messages
        messages = []
        for message in reversed(state.messages):
            if isinstance(message, ToolMessage):
                messages.append(message)
            elif len(messages) > 0 and isinstance(message, AIMessage) and len(message.tool_calls) > 0:
                messages.append(message)
            else:
                break
        messages = list(reversed(messages))

        prompt = ChatPromptTemplate.from_messages([
            ("system", "{system_prompt}"),
            MessagesPlaceholder("history"),
        ])
        model = prompt | self._llm.bind_tools(self._tools)
        response: AIMessage = await model.ainvoke({
            "system_prompt": load_prompt("answer_question", "follow_up_answering").render({
                "question": state.follow_up.question,
                "paper_title": state.preparation.title,
            }),
            "history": messages,
        })

        state.messages.append(response)
        if len(response.tool_calls) > 0:
            log.info(" * Request tools:")
            for tool_call in response.tool_calls:
                log.info("   * %s(%s)", tool_call["name"], tool_call["args"])

        else:
            log.info(" * Additional answer: %s", response.content)
            state.intermediate_answer = "\n".join(state.answers) + "\n" + response.content
            state.follow_up.question = None
            state.follow_up.is_necessary = False

        return state
