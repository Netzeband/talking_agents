from typeguard import typechecked
from langgraph.utils.runnable import RunnableCallable

from talking_agents.graph.common import ToolUsageNode as ToolUsageNode
from talking_agents.graph import INode
from talking_agents.graph.answer_question import AnswerQuestionState


class QuestionToolUsageNode(ToolUsageNode[AnswerQuestionState]):
    @typechecked()
    def __init__(
            self,
            node: INode[AnswerQuestionState],
            tools_node: RunnableCallable,
    ):
        super().__init__(
            node=node,
            tools_node=tools_node,
            state_cls=AnswerQuestionState,
            messages_attribute="messages",
            sources_attribute="sources",
        )
