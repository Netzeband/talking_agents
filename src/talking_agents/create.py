import re
import yaml
from pathlib import Path, PurePosixPath
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_experimental.text_splitter import SemanticChunker
from datetime import datetime
from pytz import timezone
from langgraph.prebuilt import ToolNode
from langchain_openai import OpenAIEmbeddings
from datetime import timedelta

from talking_agents.settings import Settings
from talking_agents.common import VectorStore
from talking_agents.common.few_shot_examples import FewShotExamples
from talking_agents.common.azure_speech_engine import create_azure_speech_engine
from talking_agents.common import VoiceConfig
from talking_agents.graph.common.languages import Languages
from talking_agents.document.section import Section, TextSection, ImageSection
from talking_agents.graph.common.setup import Persona, PodcastSetup
from talking_agents.graph.main import Graph, State, PodcastContent
from talking_agents.graph.main.nodes import PrepareNode, InterviewNode, PostProcessingNode
from talking_agents.graph.prepare.prepare_graph import PrepareGraph
from talking_agents.graph.prepare.nodes import (
    CreateTitleNode, CreateImageDescriptionsNode, CreateVectorStore, CreateIntroductionNode, CreateWrapUpNode,
    CreateTopicsNode, PrepareQuestionsNode
)
from talking_agents.graph.prepare_question.prepare_question_graph import PrepareQuestionGraph
from talking_agents.graph.interview.interview_graph import InterviewGraph
from talking_agents.graph.interview.nodes import ModeratorNode, GuestNode
from talking_agents.graph.guest.guest_graph import GuestGraph
from talking_agents.graph.guest.nodes import (
    CasualQuestionAnsweringNode, PaperQuestionAnsweringNode, GuestToolUsageNode
)
from talking_agents.graph.post_processing.post_processing_graph import PostProcessingGraph
from talking_agents.graph.post_processing.nodes import (
    CreateTranslationNode, CreateTeaserNode, RenderMarkdownNode, CreateAudioNode, AdaptInterviewNode, CreateVideoNode
)
from talking_agents.graph.prepare_question.nodes import (
    GenerateQuestionNode, AnswerQuestionsNode, AdaptQuestionsNode, GenerateFollowUpQuestionsNode
)
from talking_agents.graph.answer_question.answer_question_graph import AnswerQuestionGraph
from talking_agents.graph.answer_question.nodes import (
    QuestionRephraseNode, QuestionAnsweringNode, QuestionToolUsageNode, GroundednessEvaluation, RedoAnswerNode,
    CompletenessEvaluation, FollowUpAnswerNode, RedundancyEvaluationNode
)
from talking_agents.video_processing.audacity import Audacity
from talking_agents.video_processing.audio_mixer import AudioMixer, MixerSettings
from talking_agents.video_processing.video_mixer import VideoMixer

async def create(
        input_path: Path,
        output_path: Path,
        max_state: str,
        settings: Settings,
):
    sections = _prepare_input(input_path)


    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    vector_store = VectorStore(embeddings)
    paper_tools = [
        TavilySearchResults(max_results=2),
        vector_store.get_retrieval_tool(),
    ]
    casual_tools = [
        TavilySearchResults(max_results=2),
    ]

    questions_to_avoid_examples = FewShotExamples(
        settings.few_shot_example_path,
        "questions_to_avoid",
        k=4
    )
    prepare_graph = PrepareGraph(
        vector_store=vector_store,
        create_title_node=CreateTitleNode(
            llm=ChatOpenAI(model="gpt-4o", temperature=0.5),
        ),
        create_image_descriptions_node=CreateImageDescriptionsNode(
            llm=ChatOpenAI(model="gpt-4o", temperature=0.5),
        ),
        create_vector_store_node=CreateVectorStore(
            llm=ChatOpenAI(model="gpt-4o", temperature=0.5),
            vector_store=vector_store,
            text_splitter=SemanticChunker(embeddings),
        ),
        create_introduction_node=CreateIntroductionNode(
            llm=ChatOpenAI(model="gpt-4o", temperature=1.0),
        ),
        create_topics_node=CreateTopicsNode(
            llm=ChatOpenAI(model="gpt-4o", temperature=0.25),
        ),
        prepare_questions_node=PrepareQuestionsNode(
            prepare_question_graph=PrepareQuestionGraph(
                generate_question_node=GenerateQuestionNode(
                    llm=ChatOpenAI(model="gpt-4o", temperature=1.0),
                    question_to_avoid_examples=questions_to_avoid_examples,
                ),
                answer_question_node=AnswerQuestionsNode(
                    answer_question_graph=AnswerQuestionGraph(
                        question_rephrase_node=QuestionRephraseNode(
                            llm=ChatOpenAI(model="gpt-4o", temperature=0.5),
                            vector_store=vector_store,
                            rephrase_examples=FewShotExamples(
                                settings.few_shot_example_path,
                                "question_rephrase_examples",
                                k=4
                            ),
                        ),
                        question_answering_node=QuestionToolUsageNode(
                            node=QuestionAnsweringNode(
                                llm=ChatOpenAI(model="gpt-4o", temperature=0.5),
                                tools=paper_tools,
                            ),
                            tools_node=ToolNode(paper_tools),
                        ),
                        groundedness_evaluation_node=GroundednessEvaluation(
                            llm=ChatOpenAI(model="gpt-4o", temperature=0.0),
                        ),
                        redo_answer_node=QuestionToolUsageNode(
                            node=RedoAnswerNode(
                                llm=ChatOpenAI(model="gpt-4o", temperature=0.25),
                                tools=paper_tools,
                            ),
                            tools_node=ToolNode(paper_tools),
                        ),
                        completeness_evaluation_node=CompletenessEvaluation(
                            llm=ChatOpenAI(model="gpt-4o", temperature=0.0),
                        ),
                        follow_up_answer_node=QuestionToolUsageNode(
                            node=FollowUpAnswerNode(
                                llm=ChatOpenAI(model="gpt-4o", temperature=0.5),
                                tools=paper_tools,
                            ),
                            tools_node=ToolNode(paper_tools),
                        ),
                        redundancy_evaluation_node=RedundancyEvaluationNode(
                            llm=ChatOpenAI(model="gpt-4o", temperature=0.0),
                        ),
                        min_grounded_score=settings.min_accepted_grounded_score,
                        max_retries=settings.answer_retries,
                        max_follow_up_answers=settings.answer_follow_ups,
                    ),
                ),
                adapt_question_node=AdaptQuestionsNode(
                    llm=ChatOpenAI(model="gpt-4o", temperature=1.0),
                    question_to_avoid_examples=questions_to_avoid_examples,
                    min_accepted_grounded_score=settings.min_accepted_grounded_score,
                    max_accepted_redundancy_score=settings.max_accepted_redundancy_score,
                    max_question_retries=settings.question_retries,
                ),
                generate_follow_up_question_node=GenerateFollowUpQuestionsNode(
                    llm=ChatOpenAI(model="gpt-4o", temperature=1.0),
                    question_to_avoid_examples=questions_to_avoid_examples,
                ),
                min_accepted_grounded_score=settings.min_accepted_grounded_score,
                max_accepted_redundancy_score=settings.max_accepted_redundancy_score,
            ),
        ),
        create_wrapup_node=CreateWrapUpNode(
            llm=ChatOpenAI(model="gpt-4o", temperature=1.0),
        )
    )

    interview_guest_graph = GuestGraph(
        casual_question_answering_node=GuestToolUsageNode(
            node=CasualQuestionAnsweringNode(
                llm=ChatOpenAI(model="gpt-4o", temperature=1.0),
                tools=casual_tools,
            ),
            tools_node=ToolNode(casual_tools),
        ),
        paper_question_answering_node=PaperQuestionAnsweringNode(
            llm=ChatOpenAI(model="gpt-4o", temperature=0.5),
            min_accepted_grounded_score=settings.min_accepted_grounded_score,
        )
    )

    interview_graph = InterviewGraph(
        moderator_node=ModeratorNode(
            llm=ChatOpenAI(model="gpt-4o", temperature=1.0),
        ),
        guest_node=GuestNode(
            guest_graph=interview_guest_graph,
            min_accepted_grounded_score=settings.min_accepted_grounded_score,
        ),
    )

    post_processing_graph = PostProcessingGraph(
        create_translation_node=CreateTranslationNode(),
        create_teaser_node=CreateTeaserNode(
            llm=ChatOpenAI(model="gpt-4o", temperature=1.0),
        ),
        render_markdown_node=RenderMarkdownNode(
            min_accepted_groundedness_score=settings.min_accepted_grounded_score,
        ),
        adapt_interview_node=AdaptInterviewNode(
            llm=ChatOpenAI(model="gpt-4o", temperature=0.25),
        ),
        create_audio_node=CreateAudioNode(
            speech_engine=create_azure_speech_engine(settings),
        ),
        create_video_node=CreateVideoNode(
            audacity=Audacity(tool_path=settings.audacity_tool_path),
            audio_mixer=AudioMixer(mixer_settings=get_mixer_settings(settings.mixer_settings_file)),
            video_mixer=VideoMixer(),
            intro_music_path=settings.intro_music_path,
            outro_music_path=settings.outro_music_path,
            intro_speech_path=settings.intro_speech_path,
            podcast_image_path=settings.podcast_image_path,
        )
    )

    graph = Graph(
        prepare_node=PrepareNode(
            prepare_graph=prepare_graph,
        ),
        interview_node=InterviewNode(
            interview_graph=interview_graph,
        ),
        post_processing_node=PostProcessingNode(
            post_processing_graph=post_processing_graph,
        ),
    )

    setup = PodcastSetup(
        max_state=max_state,
        date=datetime.now(tz=timezone("Europe/Berlin")),
        episode_number=1,
        document=sections,
        document_path=PurePosixPath(input_path.as_posix()),
        paper_url="https://arxiv.org/abs/1706.03762",
        output_path=output_path,
        moderator=Persona(
            name="Frank",
            role_description=(
                "You are the moderator of a podcast with the name "
                "'Talking Agents'. In this podcast, papers are discussed and presented to the "
                "audience in a way, that they understand the underlying concepts without reading the "
                "whole paper or struggling with complicated math."
            ),
            additional_information=[
                "He is a previous AI researcher from the Munich University of Applied Sciences",
                "He is a passionate podcaster and loves to talk about AI and Machine Learning",
            ],
            private_additional_information=[
                "He is excited about Machine Learning, but mostly he appears to be professional.",
            ],
            voice={
                Languages.ENGLISH: VoiceConfig(
                    ssml='<voice name="en-US-AndrewNeural"><break time=\"250ms\" />{text}</voice>'
                )
            }
        ),
        guest=Persona(
            name="Sandra",
            role_description=(
                "You are a guest in the podcast 'Talking Agents'. In this podcast, papers "
                "are discussed and presented to the audience in a way, that they understand the underlying "
                "concepts without reading the whole paper or struggling with complicated math."
            ),
            additional_information=[
                "Institution: An AI Research Lab in Munich",
                "Position: AI Agent and Machine Learning Researcher",
#                "One of Franks favorite podcast guests",
            ],
            private_additional_information=[
                ("Likes to do a joke about AIs does not have feeling, when getting asked 'how are you?' "
                 "But **ONLY**, when she is getting asked!"),
                "She is excited about the topic.",
                ("When she get asked about the influence of transformer architectures, she likes to highlight in a "
                 "humorous way that she is an agentic AI, which also based on the transformer architecture."),
            ],
            voice={
                Languages.ENGLISH: VoiceConfig(
                    ssml='<voice name="en-US-LunaNeural"><break time=\"250ms\" />{text}</voice>'
                )
            }
        ),
        languages=[Languages.ENGLISH]
    )
    result = await graph.run(
        state=State(
            setup=setup,
            content=PodcastContent.load(
                setup.output_path,
                setup.episode_number,
                setup.languages,
            )
        )
    )

    print(" *** Finished Creating a Podcast ***")
    print(str(result.content))


def _prepare_input(input_path: Path) -> list[Section]:
    with open(input_path, "r", encoding="utf-8") as file:
        return get_document_sections(file.read())


IMAGE_SECTION_PATTERN = re.compile(r"!\[[^]]*]\(([^)]*)\)")

def get_image_path(text: str) -> PurePosixPath:
    match = re.match(IMAGE_SECTION_PATTERN, text)
    if match is None:
        raise ValueError(f"Text '{text}' does not match the image pattern")
    return PurePosixPath(match.group(1))

def get_document_sections(document: str) -> list[Section]:
    matches = re.finditer(IMAGE_SECTION_PATTERN, document)
    sections = []
    last_start = 0
    for match in matches:
        start, end = match.span()

        section_text = document[last_start:start]
        if section_text != "":
            sections.append(TextSection(text=section_text))

        section_text = document[start:end]
        if section_text != "":
            sections.append(
                ImageSection(
                    text=section_text,
                    path=get_image_path(section_text),
                )
            )

        last_start = end

    section_text = document[last_start:]
    if section_text != "":
        sections.append(TextSection(text=section_text))

    return sections

def get_mixer_settings(mixer_settings_path: Path) -> MixerSettings:
    with mixer_settings_path.open("r") as f:
        mixer_settings = yaml.safe_load(f)

    return MixerSettings(
        intro_speech_start = timedelta(milliseconds=mixer_settings["intro_speech_start"]),
        podcast_start = timedelta(milliseconds=mixer_settings["podcast_start"]),
        outro_start = timedelta(milliseconds=mixer_settings["outro_start"]),
        intro_level = mixer_settings["intro_level"],
        outro_level = mixer_settings["outro_level"],
        voice_level = mixer_settings["voice_level"],
        podcast_level = mixer_settings["podcast_level"],
    )
