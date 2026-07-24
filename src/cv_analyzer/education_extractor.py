"""
Modulo encargado de interpretar de forma inicial la formacion academica.

Convierte el bloque de formacion en objetos simples, dejando campos ambiguos
como None. La normalizacion de fechas se abordara en una etapa posterior.
"""

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class EducationEntry:
    """Formacion academica detectada de forma conservadora."""

    institution: str | None = None
    degree: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    status: str | None = None
    description: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        """Convierte la formacion en un diccionario serializable."""
        return asdict(self)


def extract_education(lines: list[str]) -> list[EducationEntry]:
    """
    Extrae formacion inicial desde las lineas de la seccion.

    Args:
        lines: Lineas de la seccion de formacion.

    Returns:
        Lista con una entrada conservadora o lista vacia.
    """
    cleaned_lines = [line.strip() for line in lines if line.strip()]
    if not cleaned_lines:
        return []

    return [EducationEntry(description="\n".join(cleaned_lines))]

