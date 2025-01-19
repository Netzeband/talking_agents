from typeguard import typechecked
from pathlib import Path
import logging
import time

from talking_agents.graph import INode
from talking_agents.graph.post_processing import PostProcessingState
from talking_agents.graph.common.post_processing_content import VideoCreationContent
from talking_agents.video_processing.audacity import Audacity
from talking_agents.video_processing.audio_mixer import AudioMixer
from talking_agents.video_processing.video_mixer import VideoMixer

log = logging.getLogger(__name__)


class CreateVideoNode(INode[PostProcessingState]):
    @typechecked()
    def __init__(
            self,
            audacity: Audacity,
            audio_mixer: AudioMixer,
            video_mixer: VideoMixer,
            intro_music_path: Path,
            outro_music_path: Path,
            intro_speech_path: Path,
            podcast_image_path: Path,
    ):
        self._audacity = audacity
        self._audio_mixer = audio_mixer
        self._video_mixer = video_mixer
        self._intro_music_path = intro_music_path
        self._outro_music_path = outro_music_path
        self._intro_speech_path = intro_speech_path
        self._podcast_image_path = podcast_image_path

    @typechecked()
    async def run(self, state: PostProcessingState) -> PostProcessingState:
        log.info("** POST-PROCESSING: CREATE VIDEO **")
        audio_processed_file_name = f"episode_{state.setup.episode_number}_{state.content.language.value}_processed.wav"
        audio_podcast_file_name = f"episode_{state.setup.episode_number}_{state.content.language.value}_podcast.wav"
        video_podcast_file_name = f"episode_{state.setup.episode_number}_{state.content.language.value}_podcast.mp4"
        state.content.video = VideoCreationContent(
            processed_audio_file=state.setup.episode_output_dir / state.content.output_path / audio_processed_file_name,
            podcast_audio_file=state.setup.episode_output_dir / state.content.output_path / audio_podcast_file_name,
            podcast_video_file=state.setup.episode_output_dir / state.content.output_path / video_podcast_file_name,
        )

        log.info("* Create processed audio file ...")
        with self._audacity as audacity:
            audacity.open_file(state.setup.episode_output_dir / state.content.audio_path)
            audacity.apply_macro("Radio-Sound")
            audacity.export_wave(state.content.video.processed_audio_file)
            time.sleep(10)

        log.info("* Mix podcast audio file ...")
        self._audio_mixer.mix(
            intro_file=self._intro_music_path,
            intro_voice_file=self._intro_speech_path,
            podcast_file=state.content.video.processed_audio_file,
            outro_file=self._outro_music_path,
            output_file=state.content.video.podcast_audio_file,
        )

        log.info("* Create podcast video file ...")
        self._video_mixer.mix(
            image_file=self._podcast_image_path,
            audio_file=state.content.video.podcast_audio_file,
            output_file=state.content.video.podcast_video_file,
        )

        return state
