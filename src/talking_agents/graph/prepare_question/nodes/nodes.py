from enum import StrEnum, auto


class PrepareQuestionNodes(StrEnum):
    GENERATE_QUESTION = auto()
    ANSWER_QUESTION = auto()
    ADAPT_QUESTION = auto()
    GENERATE_FOLLOW_UP_QUESTION = auto()
