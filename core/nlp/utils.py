import re

# Termos de TI que o Vosk frequentemente transcreve errado.
# Chave: padrão que o Vosk produz (regex, case-insensitive)
# Valor: forma correta
IT_CORRECTIONS: dict[str, str] = {
    r"\bfaia\s*ual\b": "firewall",
    r"\bfire\s*ual\b": "firewall",
    r"\bfire\s*wall\b": "firewall",
    r"\bintra\s*net\b": "intranet",
    r"\binter\s*net\b": "internet",
    r"\bback\s*end\b": "backend",
    r"\bfront\s*end\b": "frontend",
    r"\bdata\s*base\b": "database",
    r"\bdata\s*center\b": "datacenter",
    r"\bservi[çc]o\s*cloud\b": "serviço cloud",
    r"\bip\s*v\s*(?:seis|6)\b": "IPv6",
    r"\bip\s*v\s*(?:quatro|4)\b": "IPv4",
    r"\bv\s*p\s*n\b": "VPN",
    r"\bs\s*s\s*h\b": "SSH",
    r"\bs\s*s\s*l\b": "SSL",
    r"\bt\s*l\s*s\b": "TLS",
    r"\bd\s*n\s*s\b": "DNS",
    r"\bd\s*h\s*c\s*p\b": "DHCP",
    r"\bapis?\b": "API",
}


def correct_it_terms(text: str) -> str:
    """Corrige termos de TI que o Vosk frequentemente transcreve errado."""
    for pattern, replacement in IT_CORRECTIONS.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text


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
