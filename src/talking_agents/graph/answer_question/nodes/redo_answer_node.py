from typeguard import typechecked
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool
from langchain_core.messages import AIMessage, ToolMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import logging
from langchain_core.tools import tool

from src.talking_agents.graph.common.prompt import load_prompt
from src.talking_agents.graph import INode
from src.talking_agents.graph.answer_question import AnswerQuestionState

log = logging.getLogger(__name__)


class RedoAnswerNode(INode[AnswerQuestionState]):
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
        log.info("** ANSWER QUESTION: REDO ANSWER **")
        assert state.groundedness.score is not None
        assert state.groundedness.ungrounded_information is not None

        @tool(response_format="content")
        def get_summary() -> str:
            """Returns the summary of the research paper."""
            return state.preparation.summary

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
        model = prompt | self._llm.bind_tools(self._tools + [get_summary])
        response: AIMessage = await model.ainvoke({
            "system_prompt": load_prompt("answer_question", "redo_answer").render({
                "question": state.rephrased_question,
                "answer": "\n".join(
                    [f" * {a}" for a in state.answers]
                ),
                "information_without_source": "\n".join(
                    [f" * {a}" for a in state.groundedness.ungrounded_information]
                ),
            }),
            "history": messages,
        })

        state.messages.append(response)
        if len(response.tool_calls) > 0:
            log.info(" * Request tools:")
            for tool_call in response.tool_calls:
                log.info("   * %s(%s)", tool_call["name"], tool_call["args"])

        else:
            log.info(" * Intermediate answer: %s", response.content)
            state.intermediate_answer = response.content
            state.tries += 1

        return state
