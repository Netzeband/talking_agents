from enum import StrEnum, auto


class Nodes(StrEnum):
    DOWNLOAD_PAPER = auto()
    EXTRACT_DOCUMENT = auto()
    CREATE_IMAGE_DESCRIPTIONS = auto()
    CREATE_TABLE_DESCRIPTIONS = auto()
    CREATE_TITLE = auto()
    CREATE_SUMMARY = auto()
    CREATE_INTRODUCTION = auto()
    PREPARE_QUESTIONS = auto()
    CREATE_TOPICS = auto()
    CREATE_WRAP_UP = auto()
    CREATE_VECTOR_STORE = auto()
    FIND_EXAMPLES = auto()
