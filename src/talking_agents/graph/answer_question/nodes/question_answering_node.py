from typeguard import typechecked
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool
from langchain_core.messages import AIMessage, AnyMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import logging
from langchain_core.tools import tool

from src.talking_agents.graph.common.prompt import load_prompt
from src.talking_agents.graph import INode
from src.talking_agents.graph.answer_question import AnswerQuestionState
from src.talking_agents.graph.common.preparation_content import Question

log = logging.getLogger(__name__)


class QuestionAnsweringNode(INode[AnswerQuestionState]):
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
        log.info("** ANSWER QUESTION: QUESTION ANSWERING **")

        @tool(response_format="content")
        def get_summary() -> str:
            """Returns the summary of the research paper."""
            return state.preparation.summary

        assert state.rephrased_question is not None
        history = self._get_history(state.previous_questions, state.rephrased_question, state.messages)

        prompt = ChatPromptTemplate.from_messages([
            ("system", "{system_prompt}"),
            MessagesPlaceholder("history"),
        ])
        model = prompt | self._llm.bind_tools(self._tools + [get_summary])
        response: AIMessage = await model.ainvoke({
            "system_prompt": load_prompt("answer_question", "question_answering").render({
                "paper_title": state.preparation.title,
            }),
            "history": history,
        })

        state.messages.append(response)
        if len(response.tool_calls) > 0:
            log.info(" * Request tools:")
            for tool_call in response.tool_calls:
                log.info("   * %s(%s)", tool_call["name"], tool_call["args"])

        else:
            log.info(" * Intermediate answer: %s", response.content)
            state.intermediate_answer = response.content

        return state

    @staticmethod
    @typechecked()
    def _get_history(
            previous_questions: list[Question],
            rephrased_question: str,
            messages: list[AnyMessage]
    ) -> list[AnyMessage]:
        history = []
        history.append(HumanMessage(content=rephrased_question))
        return history + messages
