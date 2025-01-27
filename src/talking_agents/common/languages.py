from enum import StrEnum, auto


class Languages(StrEnum):
    ENGLISH = "en"


def get_language_name(language: Languages) -> str:
    match language:
        case Languages.ENGLISH:
            return "English"

        case _:
            raise ValueError(f"Unknown language name: {language}")
