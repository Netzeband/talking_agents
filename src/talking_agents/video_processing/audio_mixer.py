from pydantic import BaseModel
from datetime import timedelta
from typeguard import typechecked
from pathlib import Path
from pydub import AudioSegment


class MixerSettings(BaseModel):
    # calculated from beginning of intro music
    intro_speech_start: timedelta
    # calculated from end of intro music
    podcast_start: timedelta
    # calculated from end of podcast
    outro_start: timedelta
    # in dB
    intro_level: int
    # in dB
    outro_level: int
    # in dB
    voice_level: int
    # in dB
    podcast_level: int


class AudioMixer:
    @typechecked()
    def __init__(self, mixer_settings: MixerSettings):
        self._mixer_settings = mixer_settings

    @typechecked()
    def mix(
        self,
        intro_file: Path,
        intro_voice_file: Path,
        podcast_file: Path,
        outro_file: Path,
        output_file: Path,
    ):
        podcast = AudioSegment.from_wav(str(podcast_file.absolute()))
        intro_music = AudioSegment.from_wav(str(intro_file.absolute()))
        intro_voice = AudioSegment.from_wav(str(intro_voice_file.absolute()))
        outro_music = AudioSegment.from_wav(str(outro_file.absolute()))

        intro_music = intro_music + self._mixer_settings.intro_level
        outro_music = outro_music + self._mixer_settings.outro_level
        intro_voice = intro_voice + self._mixer_settings.voice_level
        podcast = podcast + self._mixer_settings.podcast_level

        start = self._mixer_settings.intro_speech_start.total_seconds() * 1000
        intro = intro_music[:start] + intro_music[start:].overlay(intro_voice)

        start = self._mixer_settings.podcast_start.total_seconds() * 1000
        mixed = intro[:start] + podcast.overlay(intro[start:])

        start = self._mixer_settings.outro_start.total_seconds() * 1000
        mixed = mixed[:start] + outro_music.overlay(mixed[start:])

        mixed.export(str(output_file), format="wav")
