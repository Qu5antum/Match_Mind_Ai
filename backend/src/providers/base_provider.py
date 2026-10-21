from abc import ABC, abstractmethod
from typing import Type
from pydantic import BaseModel


class BaseProvider(ABC):
    @abstractmethod
    def text(self, text_to_analyze: str, response_schema: Type[BaseModel]) -> BaseModel:
        pass
