from enum import StrEnum, auto


class Nodes(StrEnum):
    CREATE_TRANSLATION = auto()
    CREATE_TEASER = auto()
    RENDER_MARKDOWN = auto()
    ADAPT_INTERVIEW = auto()
    CREATE_AUDIO = auto()
    CREATE_VIDEO = auto()
