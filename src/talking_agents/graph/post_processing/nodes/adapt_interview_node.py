import re
from typeguard import typechecked
from langchain_core.language_models import BaseLanguageModel
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import logging
from html import escape
from pydantic import BaseModel, Field
from lxml import etree

from talking_agents.graph import INode
from talking_agents.graph.common.prompt import load_prompt
from talking_agents.graph.common.setup import PodcastSetup, Persona
from talking_agents.graph.post_processing import PostProcessingState
from talking_agents.graph.common.interview_content import Message, InterviewRoles

log = logging.getLogger(__name__)


class AnnotateWithSSMLOutput(BaseModel):
    ssml_text: str = Field(..., description="The text annotated with SSML")


class AdaptInterviewNode(INode[PostProcessingState]):
    @typechecked()
    def __init__(self, llm: BaseLanguageModel):
        self._llm = llm
        self._lxml_parser = etree.XMLParser(recover=True)

    @typechecked()
    async def run(self, state: PostProcessingState) -> PostProcessingState:
        log.info("** POST-PROCESSING: ADAPT INTERVIEW **")
        state.content.audio_adapted_interview = [
            await self._adapt_message(state.setup, m) for m in state.content.interview
        ]
        return state

    @typechecked()
    async def _adapt_message(self, setup: PodcastSetup, message: Message) -> Message:
        persona = self._get_persona(setup, message.role)
        original_text = escape(message.text)
        # we have to be careful with that, it needs a redesign and must be disabled in some cases:
        #  * sometimes it is drastically rewriting the text and not only adding SSML tags to it
        #  * sometimes it produces invalid SSML
        #  * ToDo: Try to fix those issues
        text = ""
        while len(text) < len(original_text):
            text = await self._annotate_with_ssml(persona, original_text)

        # when there is a comma in front of the name, the speaker always makes an award break
        text = re.sub(
            r",(\s"+setup.moderator.name+")",
            r"\1",
            text
        )
        text = re.sub(
            r",(\s"+setup.guest.name+")",
            r"\1",
            text
        )

        return Message(
            role=message.role,
            text=text,
        )

    @typechecked()
    def _get_persona(self, setup: PodcastSetup, role: InterviewRoles) -> Persona:
        if role == InterviewRoles.MODERATOR:
            return setup.moderator
        elif role == InterviewRoles.GUEST:
            return setup.guest
        else:
            raise ValueError(f"Unknown role: {role}")

    @typechecked()
    async def _annotate_with_ssml(self, persona: Persona, original_text: str) -> str:
        tries = 0
        while True:
            prompt = ChatPromptTemplate.from_messages([
                ("system", "{system_prompt}"),
            ])
            model = prompt | self._llm.with_structured_output(AnnotateWithSSMLOutput)
            response: AnnotateWithSSMLOutput = await model.ainvoke({
                "system_prompt": load_prompt("post_processing", "annotate_with_ssml").render({
                    "role_description": persona.get_role_description(),
                    "additional_information": persona.get_private_additional_information(),
                    "text": original_text,
                }),
            })
            text = response.ssml_text

            # repair eventually broken xml
            doc = etree.fromstring(text, parser=self._lxml_parser)
            if doc is None:
                log.info("The produced SSML could not be parsed. Retry ...")
                if tries > 3:
                    log.warning("Not able to produce correct SSML!")
                    return original_text
                tries += 1
                continue

            # delete some tags from SSML:
            #  * prosody tags, since they often sound strange (strong speed change in talking)
            etree.strip_tags(doc, "prosody")

            text = etree.tostring(doc).decode("utf-8")

            # remove speak tags, because they are not allowed at this level
            text = text.replace("<speak>", "")
            text = text.replace("</speak>", "")
            # we finished, so we can break the loop here
            break

        return text
