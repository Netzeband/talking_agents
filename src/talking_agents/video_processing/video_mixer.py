from typeguard import typechecked
from pathlib import Path
from moviepy import ImageClip, AudioFileClip


class VideoMixer:
    @typechecked
    def mix(
            self,
            image_file: Path,
            audio_file: Path,
            output_file: Path,
    ):
        audio = AudioFileClip(audio_file)
        image = ImageClip(image_file, duration=audio.duration)
        image.audio = audio

        video = image
        video.write_videofile(output_file, fps=24)
