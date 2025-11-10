import re, unicodedata

DEFAULT_MARKERS = [
    "VER MÁS",
    "LEA TAMBIÉN",
    "MIRA ESTO",
    "TAMBIÉN PUEDE LEER",
    "TE PUEDE INTERESAR",
    "VIDEO RECOMENDADO",
    "PUEDE LEER",
    "EN VIDEO",
    "VEA ESTO TAMBIÉN",
    "MIRE ESTO TAMBIÉN",
    "MIRA",
    "PUEDES VER",
    "LEA MÁS",
    "VER TAMBIÉN",
    "SIGUE LEYENDO",
    "MÁS INFORMACIÓN",
    "RELACIONADO",
    "PUEDE INTERESARTE",
    "NO TE PIERDAS",
    "VER VIDEO",
    "MIRA EL VIDEO",
    "VIDEO",
    "FOTO",
    "GALERÍA",
    "AMPLIAR FOTO"
]

def strip_accents(s: str) -> str:
    if not isinstance(s, str):
        return ""
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")

def regex_clean(s: str) -> str:
    if not isinstance(s, str):
        return ""
    s = s.lower()
    s = strip_accents(s)
    s = re.sub(r'https?://\S+|www\.\S+', ' ', s)
    s = re.sub(r'\S*\.(com|net|org|edu|gov|pe|es)\S*', ' ', s)
    s = re.sub(r'@\w+|#\w+', ' ', s)
    s = re.sub(r'["""\'\'`´«»]', ' ', s)
    s = re.sub(r'\d+', ' ', s)                        
    s = re.sub(r'[^a-z\s]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def remove_markers(texto: str, quitar_segmento=False, markers=None) -> str:
    if markers is None:
        markers = DEFAULT_MARKERS
    if not markers:
        return texto
    escaped_markers = [re.escape(m).replace(r"\ ", r"\s+") for m in markers]
    MARKERS_ALT = "|".join(escaped_markers)
    PAT_MARCADORES = re.compile(
        rf"(?i)\b(?:{MARKERS_ALT})\b(?:\s*[:;–—-])?"
    )
    PAT_VIDEO_PARENS = re.compile(r"(?i)[\(\[\{]\s*(?:video|foto|imagen|galería)\s*[\)\]\}]")

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

def clean_text(text, quitar_segmento=True):
    text = remove_markers(text, quitar_segmento=quitar_segmento)
    text = regex_clean(text)
    return text

def format_sentence(tokens: list, capitalize_first: bool = True, add_final_punct: bool = True) -> str:
    sentence = " ".join([t for t in tokens if t is not None])
    for punct in ['.', ',', '!', '?', ':', ';']:
        sentence = sentence.replace(f" {punct}", punct)
    sentence = sentence.strip()
    if add_final_punct and sentence and sentence[-1] not in ".!?":
        sentence += "."
    if capitalize_first and sentence and len(sentence) > 0:
        sentence = sentence[0].upper() + sentence[1:]
    
    return sentence