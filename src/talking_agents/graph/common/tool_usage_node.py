from typeguard import typechecked
from typing import Any
from langgraph.graph import StateGraph, START, END
from langgraph.utils.runnable import RunnableCallable
from langchain_core.messages import AIMessage, BaseMessage, ToolMessage
from enum import StrEnum, auto
import logging

from talking_agents.graph.interface_node import INode, TState

log = logging.getLogger(__name__)


class ToolNodes(StrEnum):
    NODE = auto()
    TOOLS = auto()


class ToolUsageNode(INode[TState]):
    @typechecked()
    def __init__(
            self,
            node: INode[TState],
            tools_node: RunnableCallable,
            state_cls: type[TState],
            messages_attribute: str | list[str],
            sources_attribute: str | list[str] | None = None,
    ):
        """
        :param node: A node, which can use tools.
        :param tools_node: A node, which processes the tool calls and stores the results in ToolMessage objects.
        :param messages_attribute: An attribute name (or a list of attribute names), which defines, where the messages
                                  are stored.
        :param sources_attribute: An optional attribute name (or a list of attribute names), which defines, where the
                                 sources are stored. If this is None, no source will be stored.
        """
        self._state_cls = state_cls
        self._messages_attribute = messages_attribute
        self._sources_attribute = sources_attribute

        async def store_tool_sources(state: TState) -> TState:
            sources = self._get_sources(state)
            if sources is not None:
                messages = self._get_messages(state)
                for message in reversed(messages):
                    if isinstance(message, ToolMessage):
                        if message.content not in sources:
                            sources.append(message.content)
                    else:
                        break

            return await node.run(state)

        graph_builder = StateGraph(self._state_cls)
        graph_builder.add_node(ToolNodes.NODE, store_tool_sources)
        graph_builder.add_node(ToolNodes.TOOLS, tools_node)

        graph_builder.add_edge(START, ToolNodes.NODE)
        graph_builder.add_conditional_edges(ToolNodes.NODE, self._chose_tool)
        graph_builder.add_edge(ToolNodes.TOOLS, ToolNodes.NODE)

        self._graph = graph_builder.compile()

    @typechecked()
    def _chose_tool(self, state: TState) -> ToolNodes | str:
        messages = self._get_messages(state)
        if len(messages) > 0:
            last_message = messages[-1]
            if isinstance(last_message, AIMessage) and len(last_message.tool_calls) > 0:
                return ToolNodes.TOOLS
        return END

    @typechecked()
    def _get_messages(self, state: TState) -> list[BaseMessage] | None:
        messages = self._get_attribute(state, self._messages_attribute)
        return messages

    @typechecked()
    def _get_sources(self, state: TState) -> list[str] | None:
        if self._sources_attribute is None:
            return None
        sources = self._get_attribute(state, self._sources_attribute)
        return sources

    @typechecked()
    def _get_attribute(self, obj: Any, keys: str | list[str]) -> Any | None:
        if isinstance(keys, list) and len(keys) == 1:
            keys = keys[0]

        if isinstance(keys, str):
            return getattr(obj, keys, None)

        else:
            obj = getattr(obj, keys[0], None)
            if obj is None:
                return None
            return self._get_attribute(obj, keys[1:])

    @typechecked()
    async def run(self, state: TState) -> TState:
        log.info("** TOOL USAGE NODE **")
        result = self._state_cls.model_validate(await self._graph.ainvoke(state))
        return result
