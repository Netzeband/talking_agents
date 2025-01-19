from typeguard import typechecked
from langchain_core.messages import BaseMessage

from talking_agents.graph.common.preparation_content import Question


@typechecked()
def get_question_history(
        previous_questions: list[Question],
        current_questions: list[Question],
        ModeratorMessageType: type,
        GuestMessageType: type,
) -> list[BaseMessage]:
    messages = []

    for question in (previous_questions + current_questions):
        messages.append(ModeratorMessageType(content=question.question))
        if question.answer is not None and len(question.answer) > 0:
            messages.append(GuestMessageType(content=_get_answer_string(question.answer)))

    return messages


def _get_answer_string(answer: list[str]) -> str:
    return "\n".join(f" * {a}" for a in answer)
