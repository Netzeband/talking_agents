from typeguard import typechecked
from langgraph.utils.runnable import RunnableCallable

from talking_agents.graph.common import ToolUsageNode as ToolUsageNode
from talking_agents.graph import INode
from talking_agents.graph.guest import GuestState


class GuestToolUsageNode(ToolUsageNode[GuestState]):
    @typechecked()
    def __init__(
            self,
            node: INode[GuestState],
            tools_node: RunnableCallable,
    ):
        super().__init__(
            node=node,
            tools_node=tools_node,
            state_cls=GuestState,
            messages_attribute="messages",
            sources_attribute="sources",
        )
