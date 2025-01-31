from enum import StrEnum, auto


class Nodes(StrEnum):
    DOWNLOAD_PAPER = auto()
    EXTRACT_DOCUMENT = auto()
    CREATE_TITLE = auto()
    CREATE_INTRODUCTION = auto()
    PREPARE_QUESTIONS = auto()
    CREATE_TOPICS = auto()
    CREATE_WRAP_UP = auto()
    CREATE_IMAGE_DESCRIPTIONS = auto()
    CREATE_VECTOR_STORE = auto()
    CREATE_SUMMARIES = auto()
