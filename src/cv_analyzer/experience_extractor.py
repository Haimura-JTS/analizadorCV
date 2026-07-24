"""
Modulo encargado de interpretar de forma inicial la seccion de experiencia.

Convierte lineas de experiencia en objetos simples, conservando descripciones
sin inventar empresa, puesto ni fechas cuando no hay certeza suficiente.

No normaliza fechas ni clasifica logros de forma avanzada.
"""

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ExperienceEntry:
    """Experiencia profesional detectada de forma conservadora."""

    company: str | None = None
    position: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    current: bool = False
    description: str | None = None
    responsibilities: list[str] | None = None
    achievements: list[str] | None = None

    def to_dict(self) -> dict[str, object]:
        """Convierte la experiencia en un diccionario serializable."""
        data = asdict(self)
        data["responsibilities"] = self.responsibilities or []
        data["achievements"] = self.achievements or []
        return data


def extract_experience(lines: list[str]) -> list[ExperienceEntry]:
    """
    Extrae experiencias iniciales desde las lineas de la seccion.

    La heuristica agrupa todo el bloque como una unica experiencia hasta que
    exista una regla mas precisa de separacion en etapas posteriores.

    Args:
        lines: Lineas de la seccion de experiencia.

    Returns:
        Lista con una experiencia o lista vacia si no hay contenido.
    """
    cleaned_lines = _remove_empty_lines(lines)
    if not cleaned_lines:
        return []

    return [
        ExperienceEntry(
            description="\n".join(cleaned_lines),
            responsibilities=_extract_bullet_lines(cleaned_lines),
            achievements=[],
        )
    ]


def _remove_empty_lines(lines: list[str]) -> list[str]:
    return [line.strip() for line in lines if line.strip()]


def _extract_bullet_lines(lines: list[str]) -> list[str]:
    bullet_prefixes = ("-", "*", "•")
    return [
        line.lstrip("-*• ").strip()
        for line in lines
        if line.lstrip().startswith(bullet_prefixes)
    ]

