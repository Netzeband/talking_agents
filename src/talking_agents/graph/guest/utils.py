from typeguard import typechecked
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage


@typechecked()
def get_conversation_history_string(history: list[BaseMessage]) -> str:
    output = ""
    for message in history:
        if isinstance(message, HumanMessage):
            output += f"_Moderator_: {message.content}\n"

        elif isinstance(message, AIMessage):
            output += f"_You_: {message.content}\n"

    return output
