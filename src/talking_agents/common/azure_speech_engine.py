from pathlib import Path
import azure.cognitiveservices.speech as speechsdk
from html import escape
from tempfile import TemporaryDirectory
import wave
import time
from typeguard import typechecked
import logging

from talking_agents.settings import Settings
from .interface_speech_engine import ISpeechEngine, SpeechText, SpeechEngineError, VoiceConfig

log = logging.getLogger(__name__)


class AzureSpeechEngine(ISpeechEngine):
    def __init__(
            self,
            speech_synthesizer: speechsdk.SpeechSynthesizer,
    ):
        self._speech_synthesizer = speech_synthesizer
        self._is_first_request = True

    @typechecked()
    def text_to_file(self, text: list[SpeechText], file: Path):
        self._is_first_request = True
        with TemporaryDirectory() as temp_dir:
            base_path = Path(temp_dir)
            chunks = []
            chunk_number = 0
            chunk_files = []
            for t in text:
                chunks.append(t)
                if len(chunks) >= 4:
                    self._text_to_file(chunks, base_path / f"chunk_{chunk_number}.wav")
                    chunk_files.append(base_path / f"chunk_{chunk_number}.wav")
                    chunk_number += 1
                    chunks = []

            if len(chunks) > 0:
                self._text_to_file(chunks, base_path / f"chunk_{chunk_number}.wav")
                chunk_files.append(base_path / f"chunk_{chunk_number}.wav")

            self._merge_wave_files(chunk_files, file)

    @typechecked()
    def _merge_wave_files(self, input_files: list[Path], output_file: Path):
        data = []
        for input_file in input_files:
            with wave.open(str(input_file), "rb") as w:
                data.append([w.getparams(), w.readframes(w.getnframes())])

        with wave.open(str(output_file), "wb") as w:
            w.setparams(data[0][0])
            for d in data:
                w.writeframes(d[1])

    @typechecked()
    def _text_to_file(self, text: list[SpeechText], file: Path):
        if not self._is_first_request:
            time.sleep(30)
        statements = []
        for message in text:
            message_text = message.text
            if not message.is_escaped:
                message_text = escape(message_text)
            statements.append(message.voice_config.ssml.format(text=message_text))
        ssml_text = "\n".join(statements)

        speech_synthesis_result = self._speech_synthesizer.speak_ssml_async(
            '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">\n' + ssml_text + '\n</speak>'
        ).get()

        if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            log.info(f"Generate output file '{file}'")
            stream = speechsdk.AudioDataStream(speech_synthesis_result)
            stream.save_to_wav_file(str(file))

        elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_synthesis_result.cancellation_details
            error = "Speech synthesis canceled: {}\n".format(cancellation_details.reason)
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                if cancellation_details.error_details:
                    error += "Error details: {}\n".format(cancellation_details.error_details)
                    error += "Did you set the speech resource key and region values?"
            log.error(error)
            raise SpeechEngineError(error)


def create_azure_speech_engine(settings: Settings) -> AzureSpeechEngine:
    speech_config = speechsdk.SpeechConfig(
                subscription=settings.speech_key.get_secret_value(),
                region=settings.speech_region,
            )
    speech_config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat.Riff48Khz16BitMonoPcm)
    return AzureSpeechEngine(
        speech_synthesizer=speechsdk.SpeechSynthesizer(
            speech_config=speech_config,
            audio_config=None
        )
    )
