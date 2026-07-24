"""
Modulo encargado de aplicar una estrategia inicial para datos personales.

La heuristica es deliberadamente conservadora: solo intenta detectar nombre y
titulo profesional en las primeras lineas limpias del curriculum.

No consulta fuentes externas ni completa informacion ausente.
"""

from dataclasses import dataclass
import re


# Permite nombres compuestos habituales con letras, espacios y separadores
# simples. No garantiza que la linea sea una identidad real.
NAME_LIKE_PATTERN = re.compile(
    r"^[A-Za-z\u00C1\u00C9\u00CD\u00D3\u00DA\u00DC\u00D1"
    r"\u00E1\u00E9\u00ED\u00F3\u00FA\u00FC\u00F1' -]{2,80}$"
)


@dataclass(frozen=True)
class PersonalInfo:
    """Datos personales basicos detectados de forma prudente."""

    full_name: str | None = None
    professional_title: str | None = None


def extract_initial_personal_info(lines: list[str]) -> PersonalInfo:
    """
    Extrae nombre y titulo profesional desde las primeras lineas del CV.

    La suposicion es que muchos CVs colocan el nombre en la primera linea y el
    titulo profesional en la siguiente. Si la primera linea contiene simbolos
    propios de contacto, no se considera nombre.

    Args:
        lines: Lineas limpias del curriculum.

    Returns:
        PersonalInfo con campos detectados o None.
    """
    if not lines:
        return PersonalInfo()

    first_line = lines[0]
    full_name = first_line if _is_probable_name(first_line) else None
    professional_title = lines[1] if full_name and len(lines) > 1 else None

    return PersonalInfo(
        full_name=full_name,
        professional_title=professional_title,
    )


def _is_probable_name(line: str) -> bool:
    if "@" in line or "http" in line.lower() or "www." in line.lower():
        return False

    words = line.split()
    if len(words) < 2 or len(words) > 5:
        return False

    return bool(NAME_LIKE_PATTERN.fullmatch(line))
