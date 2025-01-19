from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from pydantic import BaseModel


TState = TypeVar("TState", bound=BaseModel)


class INode(ABC, Generic[TState]):
    @abstractmethod
    async def run(self, state: TState) -> TState:
        raise NotImplementedError
