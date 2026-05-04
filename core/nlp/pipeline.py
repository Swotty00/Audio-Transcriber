import logging
from dataclasses import replace

from core.nlp.utils import (
    capitalize_sentences,
    clean_text,
    ensure_ending_punctuation,
    merge_short_segments,
)
from core.speech_to_text.base import Segment, Transcript

logger = logging.getLogger(__name__)


class NLPPipeline:
    def process(self, transcript: Transcript) -> Transcript:
        if not transcript.segments:
            return transcript

        logger.info("Aplicando NLP em %d segmentos.", len(transcript.segments))

        # 1. Converte segmentos para dicts, funde os muito curtos
        raw = [
            {
                "start": s.start,
                "end": s.end,
                "text": s.text,
                "confidence": s.confidence,
            }
            for s in transcript.segments
        ]
        merged = merge_short_segments(raw)

        # 2. Aplica limpeza e formatação texto a texto
        segments = []
        for seg in merged:
            text = clean_text(seg["text"])
            text = capitalize_sentences(text)
            text = ensure_ending_punctuation(text)
            segments.append(
                Segment(
                    start=seg["start"],
                    end=seg["end"],
                    text=text,
                    confidence=seg["confidence"],
                )
            )

        logger.info("NLP concluído: %d segmentos finais.", len(segments))
        return replace(transcript, segments=segments)
