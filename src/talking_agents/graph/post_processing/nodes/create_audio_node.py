from typeguard import typechecked
import logging

from src.talking_agents.common import SpeechText, VoiceConfig
from src.talking_agents.common.interface_speech_engine import ISpeechEngine
from src.talking_agents.graph import INode
from src.talking_agents.graph.common.interview_content import InterviewRoles
from src.talking_agents.graph.post_processing import PostProcessingState

log = logging.getLogger(__name__)


class CreateAudioNode(INode[PostProcessingState]):
    @typechecked()
    def __init__(self, speech_engine: ISpeechEngine):
        self._speech_engine = speech_engine

    @typechecked()
    async def run(self, state: PostProcessingState) -> PostProcessingState:
        log.info("** POST-PROCESSING: CREATE AUDIO **")
        moderator_voice = state.setup.moderator.voice[state.content.language]
        guest_voice = state.setup.guest.voice[state.content.language]

        file_name = f"episode_{state.setup.episode_number}_{state.content.language.value}.wav"
        audio_path = state.content.output_path / file_name
        full_audio_path = state.setup.episode_output_dir / audio_path
        full_audio_path.parent.mkdir(exist_ok=True, parents=True)

        self._speech_engine.text_to_file(
            self._get_speech_text(state, moderator_voice, guest_voice),
            full_audio_path
        )

        log.info(f" * Generated audio file: {audio_path}")
        state.content.audio_path = audio_path

        return state


    @typechecked()
    def _get_speech_text(
            self,
            state: PostProcessingState,
            moderator_voice: VoiceConfig,
            guest_voice: VoiceConfig,
    ) -> list[SpeechText]:
        speech_text = []
        for message in state.content.audio_adapted_interview:
            if message.role == InterviewRoles.MODERATOR:
                speech_text.append(SpeechText(text=message.text, voice_config=moderator_voice, is_escaped=True))
            elif message.role == InterviewRoles.GUEST:
                speech_text.append(SpeechText(text=message.text, voice_config=guest_voice, is_escaped=True))
            else:
                raise ValueError(f"Unknown role: {message.role}")

        return speech_text
