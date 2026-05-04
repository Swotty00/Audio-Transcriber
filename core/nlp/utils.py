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
    """Funde segmentos com menos de `min_words` palavras.
    Segmentos curtos no início fundem com o próximo; demais fundem com o anterior.
    """
    if not segments:
        return segments

    result: list[dict] = []
    for seg in segments:
        is_short = len(seg["text"].split()) < min_words
        if is_short and result:
            # funde no anterior
            prev = result[-1]
            result[-1] = {
                "start": prev["start"],
                "end": seg["end"],
                "text": prev["text"].rstrip(".") + " " + seg["text"],
                "confidence": (prev["confidence"] + seg["confidence"]) / 2,
            }
        elif is_short and not result:
            # primeiro segmento é curto — guarda para fundir com o próximo
            result.append(seg)
        elif not is_short and result and len(result[-1]["text"].split()) < min_words:
            # anterior estava pendente por ser curto — funde nele
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
