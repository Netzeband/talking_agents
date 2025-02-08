from typeguard import typechecked
import logging
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import SystemMessage, BaseMessage
from langchain_core.output_parsers import StrOutputParser

from src.talking_agents.graph.common.prompt import load_prompt
from src.talking_agents.graph import INode
from src.talking_agents.graph.guest import GuestState

log = logging.getLogger(__name__)


class PaperQuestionAnsweringNode(INode):
    @typechecked
    def __init__(self, llm: BaseChatModel, min_accepted_grounded_score: float):
        self._llm = llm
        self._minimum_accepted_grounded_score = min_accepted_grounded_score

    @typechecked()
    async def run(self, state: GuestState):
        assert state.next_question >= 0 and state.next_question < len(state.preparation.questions)

        log.info("** GUEST: PAPER QUESTION ANSWERING **")
        prompt = ChatPromptTemplate.from_messages([
            ("system", load_prompt("guest", "paper_question_answering").render({
                "role_description": state.setup.guest.get_role_description(),
                "role_information": state.setup.guest.get_private_additional_information(),
                "moderator_name": state.setup.moderator.name,
                "moderator_finished": state.is_moderator_finished,
            })),
            MessagesPlaceholder("history"),
        ])
        model = prompt | self._llm | StrOutputParser()
        response = await model.ainvoke({
            "history": state.history + self._get_ai_assistant_message(state)
        })
        state.answer = response
        state.answer_groundedness = state.preparation.questions[state.next_question].groundedness
        state.answer_redundancy = state.preparation.questions[state.next_question].redundancy
        state.topic = state.preparation.questions[state.next_question].topic
        state.sources = state.preparation.questions[state.next_question].metadata.get("sources", None)

        log.info(" * Answer: %s", state.answer)
        state.is_finished = False
        return state

    @typechecked()
    def _get_ai_assistant_message(self, state: GuestState) -> list[BaseMessage]:
        question = state.preparation.questions[state.next_question]
        if question.groundedness.score is not None:
            if question.groundedness.score < self._minimum_accepted_grounded_score:
                return [SystemMessage(
                    content="THE ANSWER CANNOT BE FOUND IN THE PAPER! TELL THE MODERATOR TO ASK ANOTHER QUESTION!"
                )]

        return [SystemMessage(
            content=load_prompt("guest", "ai_assistant_message").render({
                "new_information": "\n".join([f" * {i}" for i in question.redundancy.new_information]),
                "known_information": "\n".join([f" * {i}" for i in question.redundancy.old_information]),
            })
        )]
