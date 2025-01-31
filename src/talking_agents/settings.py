from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import AnyUrl, SecretStr


class Settings(BaseSettings):
    langchain_tracing_v2: bool | None = None
    langchain_endpoint: AnyUrl | None = None
    langchain_api_key: SecretStr | None = None
    langchain_project: str | None = None
    unstructured_api_key: str
    unstructured_api_url: str
    speech_key: SecretStr
    speech_region: str
    openai_api_key: SecretStr
    min_accepted_grounded_score: float
    max_accepted_redundancy_score: float
    answer_retries: int
    answer_follow_ups: int
    question_retries: int
    few_shot_example_path: Path
    audacity_tool_path: Path
    mixer_settings_file: Path
    intro_music_path: Path
    outro_music_path: Path
    intro_speech_path: Path
    podcast_image_path: Path

    class Config:
        env_file = '.env'
