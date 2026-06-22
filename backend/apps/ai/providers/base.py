from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class DraftResult:
    headline: str
    description: str


@dataclass
class TranslationResult:
    headline: str
    description: str


class AIProvider(ABC):
    @abstractmethod
    def generate_draft(self, brief: str) -> DraftResult:
        ...

    @abstractmethod
    def translate(self, text: str, target_language: str) -> TranslationResult:
        ...
