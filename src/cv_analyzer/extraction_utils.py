"""
Utilidades compartidas por los extractores de secciones estructuradas.

Centraliza la deteccion de vinetas, listas y fragmentos de fecha para evitar
reglas duplicadas entre experiencia, formacion y secciones adicionales.

No decide que texto representa una empresa, un puesto o una institucion.
"""

from collections.abc import Iterable
from dataclasses import dataclass
import re
import unicodedata

from cv_analyzer.date_normalizer import normalize_date, normalize_date_range


# Reconoce los marcadores de lista mas frecuentes extraidos desde un PDF.
BULLET_PREFIX_PATTERN = re.compile(r"^\s*[-*\u2022\u25AA\u25E6]\s+")

# Reconoce fechas parciales ya soportadas por date_normalizer dentro de una
# linea mayor. No interpreta dias ni estaciones del ano.
DATE_VALUE_FRAGMENT = (
    r"(?:"
    r"[A-Za-z\u00C0-\u017F]+\.?\s+\d{4}"
    r"|\d{1,2}/\d{4}"
    r"|\d{4}[-/]\d{1,2}"
    r"|\d{4}"
    r")"
)
DATE_RANGE_FRAGMENT_PATTERN = re.compile(
    rf"(?P<range>{DATE_VALUE_FRAGMENT}"
    rf"\s+(?:-|\u2013|\u2014|a|to)\s+"
    rf"(?:{DATE_VALUE_FRAGMENT}|actualidad|actual|presente|present|current)\b)",
    re.IGNORECASE,
)
SINGLE_DATE_FRAGMENT_PATTERN = re.compile(
    rf"(?<!\d)(?P<date>{DATE_VALUE_FRAGMENT})(?!\d)",
    re.IGNORECASE,
)

# Separa listas explicitas sin dividir guiones internos de nombres o productos.
VALUE_SEPARATOR_PATTERN = re.compile(r"[,;|]")


@dataclass(frozen=True)
class ExtractedDateRange:
    """Rango localizado y normalizado dentro de una linea."""

    raw: str
    start_date: str
    end_date: str | None
    current: bool


def clean_nonempty_lines(lines: Iterable[str]) -> list[str]:
    """Devuelve lineas sin espacios exteriores ni elementos vacios."""
    return [line.strip() for line in lines if line.strip()]


def is_bullet_line(line: str) -> bool:
    """Indica si una linea comienza con una vineta reconocida."""
    return BULLET_PREFIX_PATTERN.match(line) is not None


def strip_bullet(line: str) -> str:
    """Retira una unica vineta inicial y conserva el contenido restante."""
    return BULLET_PREFIX_PATTERN.sub("", line, count=1).strip()


def find_date_range(text: str) -> ExtractedDateRange | None:
    """
    Localiza un rango conocido dentro de una linea.

    Devuelve None cuando el fragmento coincide superficialmente pero el
    normalizador no puede interpretarlo con certeza.
    """
    match = DATE_RANGE_FRAGMENT_PATTERN.search(text)
    if match is None:
        return None

    raw_range = match.group("range")
    normalized_range = normalize_date_range(raw_range)
    if normalized_range.start_date is None:
        return None
    if normalized_range.end_date is None and not normalized_range.current:
        return None

    return ExtractedDateRange(
        raw=raw_range,
        start_date=normalized_range.start_date,
        end_date=normalized_range.end_date,
        current=normalized_range.current,
    )


def find_single_date(text: str) -> tuple[str, str] | None:
    """Localiza una fecha parcial conocida y devuelve fragmento y valor."""
    match = SINGLE_DATE_FRAGMENT_PATTERN.search(text)
    if match is None:
        return None

    raw_date = match.group("date")
    normalized_date = normalize_date(raw_date)
    if normalized_date is None:
        return None

    return raw_date, normalized_date


def split_values(text: str) -> list[str]:
    """Separa valores por coma, punto y coma o barra vertical."""
    return [
        value.strip()
        for value in VALUE_SEPARATOR_PATTERN.split(text)
        if value.strip()
    ]


def deduplicate_preserving_order(values: Iterable[str]) -> list[str]:
    """Elimina duplicados sin distinguir mayusculas y conserva el orden."""
    seen_values: set[str] = set()
    result: list[str] = []

    for value in values:
        normalized_value = value.casefold()
        if normalized_value in seen_values:
            continue
        seen_values.add(normalized_value)
        result.append(value)

    return result


def normalize_lookup_text(value: str) -> str:
    """Normaliza mayusculas y diacriticos para comparar vocabularios."""
    decomposed_value = unicodedata.normalize("NFD", value.strip().casefold())
    return "".join(
        character
        for character in decomposed_value
        if unicodedata.category(character) != "Mn"
    )
