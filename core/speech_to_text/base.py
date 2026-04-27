from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class Segment:
    start: float
    end: float
    text: str
    confidence: float = 1.0


@dataclass
class Transcript:
    segments: list[Segment] = field(default_factory=list)
    language: str = "pt"

    @property
    def full_text(self) -> str:
        return " ".join(s.text for s in self.segments if s.text.strip())

    @property
    def duration(self) -> float:
        if not self.segments:
            return 0.0
        return self.segments[-1].end


class SpeechToTextEngine(ABC):
    @abstractmethod
    def transcribe(self, wav_path: str) -> Transcript: ...

    @abstractmethod
    def is_ready(self) -> bool: ...
