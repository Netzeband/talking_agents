from enum import StrEnum, auto


class AnswerQuestionNodes(StrEnum):
    QUESTION_REPHRASE = auto()
    QUESTION_ANSWERING = auto()
    SEARCH_EXAMPLE = auto()
    GROUNDEDNESS_EVALUATION = auto()
    REDO_ANSWER = auto()
    COMPLETENESS_EVALUATION = auto()
    FOLLOW_UP_ANSWER = auto()
    REDUNDANCY_EVALUATION = auto()
