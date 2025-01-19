from pathlib import PurePosixPath
from pydantic import BaseModel


class Section(BaseModel):
    text: str


class TextSection(Section):
    pass


class ImageSection(Section):
    path: PurePosixPath
