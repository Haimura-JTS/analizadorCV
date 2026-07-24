"""
Modulo encargado de normalizar fechas detectadas en curriculums.

Reconoce formatos frecuentes en espanol e ingles y devuelve fechas parciales
sin completar informacion inexistente. Cuando no hay certeza suficiente,
devuelve None y deja que el validador registre la advertencia correspondiente.

No extrae fechas desde texto largo ni decide duraciones laborales.
"""

from dataclasses import dataclass
import re
import unicodedata


# Reconoce rangos con separadores visibles entre dos fechas.
# No divide fechas ISO como 2024-01 porque exige espacios alrededor.
DATE_RANGE_SEPARATOR_PATTERN = re.compile(
    "\\s+(?:-|\\u2013|\\u2014|a|to)\\s+"
)

# Reconoce formatos numericos como 2024-01 o 2024/01.
YEAR_MONTH_PATTERN = re.compile(
    r"^(?P<year>\d{4})[-/](?P<month>0?[1-9]|1[0-2])$"
)

# Reconoce formatos numericos como 01/2024.
MONTH_YEAR_PATTERN = re.compile(
    r"^(?P<month>0?[1-9]|1[0-2])/(?P<year>\d{4})$"
)

# Reconoce anos aislados. No interpreta anos fuera de cuatro digitos.
YEAR_PATTERN = re.compile(r"^\d{4}$")

# Reconoce formatos como enero 2024, ene. 2024, Jan 2024 o January 2024.
TEXTUAL_MONTH_PATTERN = re.compile(
    r"^(?P<month>[a-z.]+)\s+(?P<year>\d{4})$"
)


MONTH_ALIASES = {
    "enero": "01",
    "ene": "01",
    "january": "01",
    "jan": "01",
    "febrero": "02",
    "feb": "02",
    "february": "02",
    "marzo": "03",
    "mar": "03",
    "march": "03",
    "abril": "04",
    "abr": "04",
    "april": "04",
    "apr": "04",
    "mayo": "05",
    "may": "05",
    "junio": "06",
    "jun": "06",
    "june": "06",
    "julio": "07",
    "jul": "07",
    "july": "07",
    "agosto": "08",
    "ago": "08",
    "august": "08",
    "aug": "08",
    "septiembre": "09",
    "setiembre": "09",
    "sep": "09",
    "sept": "09",
    "september": "09",
    "octubre": "10",
    "oct": "10",
    "october": "10",
    "noviembre": "11",
    "nov": "11",
    "november": "11",
    "diciembre": "12",
    "dic": "12",
    "december": "12",
    "dec": "12",
}

CURRENT_DATE_ALIASES = {
    "actual",
    "actualidad",
    "presente",
    "present",
    "current",
}


@dataclass(frozen=True)
class NormalizedDateRange:
    """
    Resultado de normalizar un rango de fechas.

    Args:
        start_date: Fecha inicial normalizada o None.
        end_date: Fecha final normalizada o None.
        current: True si el rango indica actualidad.
        warnings: Advertencias detectadas durante la normalizacion.
    """

    start_date: str | None
    end_date: str | None
    current: bool
    warnings: list[str]


def normalize_date(value: str | None) -> str | None:
    """
    Normaliza una fecha parcial conocida.

    Args:
        value: Fecha en texto libre corto.

    Returns:
        `YYYY-MM`, `YYYY` o None si el formato no es suficientemente claro.
    """
    if value is None:
        return None

    normalized_value = _normalize_lookup_text(value)
    if not normalized_value:
        return None

    if YEAR_PATTERN.fullmatch(normalized_value):
        return normalized_value

    year_month_match = YEAR_MONTH_PATTERN.fullmatch(normalized_value)
    if year_month_match:
        return _format_year_month(
            year_month_match.group("year"),
            year_month_match.group("month"),
        )

    month_year_match = MONTH_YEAR_PATTERN.fullmatch(normalized_value)
    if month_year_match:
        return _format_year_month(
            month_year_match.group("year"),
            month_year_match.group("month"),
        )

    textual_month_match = TEXTUAL_MONTH_PATTERN.fullmatch(normalized_value)
    if textual_month_match:
        month = MONTH_ALIASES.get(
            textual_month_match.group("month").removesuffix(".")
        )
        if month is None:
            return None
        return f"{textual_month_match.group('year')}-{month}"

    return None


def normalize_date_range(value: str | None) -> NormalizedDateRange:
    """
    Normaliza un rango de fechas corto.

    Args:
        value: Rango como `2023 - Actualidad` o `Jan 2023 - Mar 2024`.

    Returns:
        Rango normalizado y advertencias si alguna parte es ambigua.
    """
    if value is None or not value.strip():
        return NormalizedDateRange(None, None, False, ["Rango de fechas vacio."])

    parts = DATE_RANGE_SEPARATOR_PATTERN.split(value.strip(), maxsplit=1)
    if len(parts) == 1:
        start_date = normalize_date(parts[0])
        warnings = [] if start_date else [f"Fecha ambigua: {value}."]
        return NormalizedDateRange(start_date, None, False, warnings)

    start_raw, end_raw = parts
    start_date = normalize_date(start_raw)
    normalized_end = _normalize_lookup_text(end_raw)
    current = normalized_end in CURRENT_DATE_ALIASES
    end_date = None if current else normalize_date(end_raw)
    warnings: list[str] = []

    if start_date is None:
        warnings.append(f"Fecha inicial ambigua: {start_raw}.")
    if end_date is None and not current:
        warnings.append(f"Fecha final ambigua: {end_raw}.")

    return NormalizedDateRange(start_date, end_date, current, warnings)


def _format_year_month(year: str, month: str) -> str:
    return f"{year}-{int(month):02d}"


def _normalize_lookup_text(value: str) -> str:
    stripped_value = value.strip().lower().replace(".", "")
    decomposed_value = unicodedata.normalize("NFD", stripped_value)
    return "".join(
        character
        for character in decomposed_value
        if unicodedata.category(character) != "Mn"
    )

