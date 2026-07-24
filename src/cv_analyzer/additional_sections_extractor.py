"""
Modulo encargado de extraer secciones adicionales del curriculum.

Incluye idiomas, certificaciones, cursos y proyectos con reglas iniciales
conservadoras. No normaliza fechas ni valida niveles todavia.
"""

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class LanguageEntry:
    """Idioma detectado en el curriculum."""

    language: str | None = None
    level: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        """Convierte el idioma en un diccionario serializable."""
        return asdict(self)


@dataclass(frozen=True)
class CertificationEntry:
    """Certificacion detectada en el curriculum."""

    name: str | None = None
    institution: str | None = None
    date: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        """Convierte la certificacion en un diccionario serializable."""
        return asdict(self)


@dataclass(frozen=True)
class CourseEntry:
    """Curso detectado en el curriculum."""

    name: str | None = None
    institution: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    status: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        """Convierte el curso en un diccionario serializable."""
        return asdict(self)


@dataclass(frozen=True)
class ProjectEntry:
    """Proyecto detectado en el curriculum."""

    name: str | None = None
    description: str | None = None
    technologies: list[str] | None = None
    url: str | None = None

    def to_dict(self) -> dict[str, object]:
        """Convierte el proyecto en un diccionario serializable."""
        data = asdict(self)
        data["technologies"] = self.technologies or []
        return data


def extract_languages(lines: list[str]) -> list[LanguageEntry]:
    """
    Extrae idiomas separando idioma y nivel cuando aparece un guion o dos puntos.

    Args:
        lines: Lineas de la seccion de idiomas.

    Returns:
        Lista de idiomas detectados.
    """
    return [
        LanguageEntry(language=language, level=level)
        for language, level in (_split_name_and_detail(line) for line in lines)
        if language
    ]


def extract_certifications(lines: list[str]) -> list[CertificationEntry]:
    """Extrae certificaciones iniciales desde lineas no vacias."""
    return [
        CertificationEntry(name=line.strip())
        for line in lines
        if line.strip()
    ]


def extract_courses(lines: list[str]) -> list[CourseEntry]:
    """Extrae cursos iniciales desde lineas no vacias."""
    return [CourseEntry(name=line.strip()) for line in lines if line.strip()]


def extract_projects(lines: list[str]) -> list[ProjectEntry]:
    """
    Extrae proyectos iniciales conservando cada linea como descripcion.

    Args:
        lines: Lineas de la seccion de proyectos.

    Returns:
        Lista de proyectos detectados.
    """
    return [
        ProjectEntry(name=line.strip(), description=line.strip())
        for line in lines
        if line.strip()
    ]


def _split_name_and_detail(line: str) -> tuple[str | None, str | None]:
    cleaned_line = line.strip().lstrip("-*\u2022 ").strip()
    if not cleaned_line:
        return None, None

    for separator in (":", "-"):
        if separator in cleaned_line:
            name, detail = cleaned_line.split(separator, maxsplit=1)
            return name.strip() or None, detail.strip() or None

    return cleaned_line, None
