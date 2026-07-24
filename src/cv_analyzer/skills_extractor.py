"""
Modulo encargado de extraer habilidades desde la seccion correspondiente.

Separa habilidades por comas, punto y coma, barras verticales y lineas. La
clasificacion avanzada queda pendiente para mantener una heuristica visible y
prudente.
"""

from collections.abc import Iterable
import re


SKILL_SEPARATOR_PATTERN = re.compile(r"[,;|]")


def extract_skills(lines: list[str]) -> dict[str, list[str]]:
    """
    Extrae habilidades tecnicas iniciales.

    Args:
        lines: Lineas de la seccion de habilidades.

    Returns:
        Diccionario compatible con el bloque `skills` del JSON objetivo.
    """
    skills = _deduplicate_preserving_order(
        skill
        for line in lines
        for skill in _split_skill_line(line)
        if skill
    )

    return {
        "technical": skills,
        "tools": [],
        "programming_languages": [],
        "soft_skills": [],
    }


def _split_skill_line(line: str) -> list[str]:
    normalized_line = line.strip().lstrip("-*\u2022 ").strip()
    return [
        skill.strip()
        for skill in SKILL_SEPARATOR_PATTERN.split(normalized_line)
        if skill.strip()
    ]


def _deduplicate_preserving_order(values: Iterable[str]) -> list[str]:
    seen_values: set[str] = set()
    result: list[str] = []

    for value in values:
        normalized_value = value.lower()
        if normalized_value in seen_values:
            continue
        seen_values.add(normalized_value)
        result.append(value)

    return result
