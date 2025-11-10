import re, unicodedata

def strip_accents(s: str) -> str:
    if not isinstance(s, str):
        return ""
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")

def regex_clean(s: str) -> str:
    if not isinstance(s, str):
        return ""
    s = s.lower()
    s = strip_accents(s)
    s = re.sub(r'https?://\S+|www\.\S+', ' ', s)      # URLs
    s = re.sub(r'@\w+|#\w+', ' ', s)                  # @menciones y #hashtags
    #s = re.sub(r'\d+', ' ', s)                        # números (opcional)
    #s = re.sub(r'[^a-z\s]', ' ', s)                   # deja solo letras y espacios
    s = re.sub(r'\s+', ' ', s).strip()                # colapsa espacios
    return s

def remove_markers(texto: str, quitar_segmento=False, markers=[]) -> str:
    MARKERS_ALT = "|".join(re.sub(r"\s+", r"\\s+", re.escape(m)) for m in markers)
    PAT_MARCADORES = re.compile(
        rf"(?i)(?:^|\s)(?:{MARKERS_ALT})(?:\s*[:;–—-]\s*)"
    )

    PAT_VIDEO_PARENS = re.compile(r"(?i)[\(\[\{]\s*video\s*[\)\]\}]")

    if not isinstance(texto, str):
        return texto
    t = texto

    t = PAT_VIDEO_PARENS.sub(" ", t)

    if quitar_segmento:
        t = re.sub(PAT_MARCADORES.pattern + r"[^\.!\?\n]{0,140}", " ", t)
    else:
        t = PAT_MARCADORES.sub(" ", t)

    t = re.sub(r"\s+", " ", t).strip()
    return t

def clean_text(text):
    return remove_markers(regex_clean(text))