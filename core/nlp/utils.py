import re


def clean_text(text: str) -> str:
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text


def capitalize_sentences(text: str) -> str:
    return re.sub(
        r"((?:^|[.!?]\s+))([a-záàãâéêíóôõúüçñ])",
        lambda m: m.group(1) + m.group(2).upper(),
        text,
        flags=re.IGNORECASE,
    )


def ensure_ending_punctuation(text: str) -> str:
    if text and text[-1] not in ".!?":
        return text + "."
    return text


def merge_short_segments(segments: list[dict], min_words: int = 2) -> list[dict]:
    """Funde segmentos com menos de `min_words` palavras no anterior."""
    if not segments:
        return segments

    result = [segments[0]]
    for seg in segments[1:]:
        if len(seg["text"].split()) < min_words and result:
            prev = result[-1]
            result[-1] = {
                "start": prev["start"],
                "end": seg["end"],
                "text": prev["text"].rstrip(".") + " " + seg["text"],
                "confidence": (prev["confidence"] + seg["confidence"]) / 2,
            }
        else:
            result.append(seg)
    return result
