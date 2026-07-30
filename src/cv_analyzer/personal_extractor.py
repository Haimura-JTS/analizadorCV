"""
Modulo encargado de aplicar una estrategia inicial para datos personales.

La heuristica es deliberadamente conservadora: solo intenta detectar nombre y
titulo profesional en las primeras lineas limpias del curriculum, descartando
encabezados, datos de contacto y terminos profesionales evidentes.

No consulta fuentes externas ni completa informacion ausente.
"""

from dataclasses import dataclass
import re

from cv_analyzer.contact_extractor import EMAIL_PATTERN, URL_PATTERN
from cv_analyzer.contact_extractor import extract_phone
from cv_analyzer.section_detector import find_section_name


# Permite nombres compuestos habituales con letras, espacios y separadores
# simples. No garantiza que la linea sea una identidad real.
NAME_LIKE_PATTERN = re.compile(
    r"^[A-Za-z\u00C1\u00C9\u00CD\u00D3\u00DA\u00DC\u00D1"
    r"\u00E1\u00E9\u00ED\u00F3\u00FA\u00FC\u00F1' -]{2,80}$"
)

MAX_HEADER_LINES_TO_INSPECT = 5
MAX_TITLE_DISTANCE = 3
MAX_TITLE_WORDS = 8
SENTENCE_ENDINGS = (".", "!", "?")
NON_NAME_HEADINGS = {
    "curriculum",
    "curriculum vitae",
    "currículum",
    "currículum vitae",
    "cv",
    "resume",
    "résumé",
}
NAME_PARTICLES = {
    "da",
    "de",
    "del",
    "do",
    "dos",
    "la",
    "las",
    "los",
    "van",
    "von",
    "y",
}
PROFESSIONAL_ROLE_TERMS = {
    "analista",
    "analyst",
    "architect",
    "arquitecto",
    "consultant",
    "consultor",
    "developer",
    "desarrollador",
    "designer",
    "diseñador",
    "engineer",
    "ingeniero",
    "manager",
    "owner",
    "scientist",
    "specialist",
    "técnico",
    "technician",
}


@dataclass(frozen=True)
class PersonalInfo:
    """Datos personales basicos detectados de forma prudente."""

    full_name: str | None = None
    professional_title: str | None = None


def extract_initial_personal_info(lines: list[str]) -> PersonalInfo:
    """
    Extrae nombre y titulo profesional desde las primeras lineas del CV.

    La suposicion es que muchos CVs colocan el nombre cerca del inicio y el
    titulo profesional poco despues. Se inspeccionan como maximo cinco lineas;
    los candidatos ambiguos se descartan.

    Args:
        lines: Lineas limpias del curriculum.

    Returns:
        PersonalInfo con campos detectados o None.
    """
    name_index = next(
        (
            index
            for index, line in enumerate(lines[:MAX_HEADER_LINES_TO_INSPECT])
            if _is_probable_name(line)
        ),
        None,
    )
    if name_index is None:
        return PersonalInfo()

    full_name = lines[name_index].strip()
    professional_title = _find_professional_title(
        lines,
        name_index=name_index,
    )

    return PersonalInfo(
        full_name=full_name,
        professional_title=professional_title,
    )


def _find_professional_title(
    lines: list[str],
    *,
    name_index: int,
) -> str | None:
    title_candidates = lines[
        name_index + 1 : name_index + 1 + MAX_TITLE_DISTANCE
    ]

    for candidate in title_candidates:
        if find_section_name(candidate) is not None:
            break
        if _is_probable_professional_title(candidate):
            return candidate.strip()

    return None


def _is_probable_name(line: str) -> bool:
    cleaned_line = line.strip()
    normalized_line = cleaned_line.casefold()

    if normalized_line in NON_NAME_HEADINGS:
        return False
    if find_section_name(cleaned_line) is not None:
        return False
    if _contains_contact_data(cleaned_line):
        return False

    words = cleaned_line.split()
    if len(words) < 2 or len(words) > 5:
        return False
    if any(
        word.casefold().strip("-'") in PROFESSIONAL_ROLE_TERMS
        for word in words
    ):
        return False
    if not _has_name_capitalization(words):
        return False

    return bool(NAME_LIKE_PATTERN.fullmatch(cleaned_line))


def _is_probable_professional_title(line: str) -> bool:
    cleaned_line = line.strip()

    if not cleaned_line or len(cleaned_line) > 120:
        return False
    if len(cleaned_line.split()) > MAX_TITLE_WORDS:
        return False
    if cleaned_line.endswith(SENTENCE_ENDINGS):
        return False
    if find_section_name(cleaned_line) is not None:
        return False
    if _contains_contact_data(cleaned_line):
        return False
    if _is_probable_name(cleaned_line):
        return False

    return True


def _contains_contact_data(line: str) -> bool:
    return (
        EMAIL_PATTERN.search(line) is not None
        or URL_PATTERN.search(line) is not None
        or extract_phone(line) is not None
    )


def _has_name_capitalization(words: list[str]) -> bool:
    for word in words:
        normalized_word = word.casefold().strip("-'")
        if normalized_word in NAME_PARTICLES:
            continue

        visible_word = word.strip("-'")
        if not visible_word:
            return False
        if not (visible_word[0].isupper() or visible_word.isupper()):
            return False

    return True
