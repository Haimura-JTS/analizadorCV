"""
Extraccion conservadora de idiomas, certificaciones, cursos y proyectos.

Las reglas aprovechan separadores y etiquetas visibles para poblar el contrato
estructurado. El texto ambiguo se conserva y genera advertencias indexadas.
"""

from dataclasses import asdict, dataclass
import re

from cv_analyzer.extraction_utils import clean_nonempty_lines, find_date_range
from cv_analyzer.extraction_utils import deduplicate_preserving_order
from cv_analyzer.extraction_utils import find_single_date, is_bullet_line
from cv_analyzer.extraction_utils import normalize_lookup_text
from cv_analyzer.extraction_utils import split_values, strip_bullet


DETAIL_SEPARATOR_PATTERN = re.compile(r"\s+(?:-|\u2013|\u2014|\|)\s+")
LANGUAGE_LEVEL_PATTERN = re.compile(
    r"^(?:[abc][12]|"
    r"advanced|avanzado|basic|basico|bilingual|bilingue|"
    r"business working proficiency|conversational|elementary|"
    r"elementary proficiency|fluent|fluido|full professional proficiency|"
    r"intermediate|intermedio|limited working proficiency|medio|"
    r"mother tongue|native|native speaker|nativo|"
    r"professional|professional working proficiency|profesional)$",
    re.IGNORECASE,
)
TRAILING_LANGUAGE_LEVEL_PATTERN = re.compile(
    r"^(?P<language>.+?)\s+"
    r"(?P<level>[ABC][12]|Advanced|Avanzado|Basic|Basico|"
    r"Intermediate|Intermedio|Native|Nativo|Fluent|Fluido|Medio|"
    r"Professional|Profesional)$",
    re.IGNORECASE,
)
PARENTHESIZED_LANGUAGE_LEVEL_PATTERN = re.compile(
    r"^(?P<language>.+?)\s*\((?P<level>[^()]+)\)$"
)
LANGUAGE_ENTRY_SEPARATOR_PATTERN = re.compile(r"\s*[,;|/]\s*")
LANGUAGE_LEVEL_PREFIX_PATTERN = re.compile(
    r"^(?:nivel|level)\s+(?:de|of)\s+(?P<language>.+?)\s*:\s*"
    r"(?P<level>.+)$",
    re.IGNORECASE,
)

PROJECT_LABELS = {
    "description": "description",
    "descripcion": "description",
    "enlace": "url",
    "link": "url",
    "name": "name",
    "nombre": "name",
    "project": "name",
    "proyecto": "name",
    "stack": "technologies",
    "tech stack": "technologies",
    "technologies": "technologies",
    "tecnologias": "technologies",
    "title": "name",
    "titulo": "name",
    "url": "url",
}


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


@dataclass(frozen=True)
class LanguageExtractionResult:
    """Idiomas detectados y advertencias asociadas."""

    entries: list[LanguageEntry]
    warnings: list[str]


@dataclass(frozen=True)
class CertificationExtractionResult:
    """Certificaciones detectadas y advertencias asociadas."""

    entries: list[CertificationEntry]
    warnings: list[str]


@dataclass(frozen=True)
class CourseExtractionResult:
    """Cursos detectados y advertencias asociadas."""

    entries: list[CourseEntry]
    warnings: list[str]


@dataclass(frozen=True)
class ProjectExtractionResult:
    """Proyectos detectados y advertencias asociadas."""

    entries: list[ProjectEntry]
    warnings: list[str]


def extract_languages(lines: list[str]) -> list[LanguageEntry]:
    """
    Extrae idiomas manteniendo la interfaz publica original.

    Args:
        lines: Lineas de la seccion de idiomas.

    Returns:
        Idiomas detectados en su orden de aparicion.
    """
    return extract_languages_with_warnings(lines).entries


def extract_languages_with_warnings(
    lines: list[str],
) -> LanguageExtractionResult:
    """
    Extrae idiomas y niveles mediante separadores o niveles finales conocidos.

    Una lista sin niveles, como `English, Spanish`, produce dos idiomas. Un
    detalle explicito desconocido se conserva y se marca como ambiguo.
    """
    entries: list[LanguageEntry] = []
    warnings: list[str] = []

    for line in clean_nonempty_lines(lines):
        cleaned_line = _clean_list_line(line)
        for language_item in _split_language_items(cleaned_line):
            language, level, explicit_detail = _split_language_and_level(
                language_item
            )
            if explicit_detail and language is None:
                entries.append(LanguageEntry(level=level))
                warnings.append(
                    f"languages[{len(entries) - 1}] no incluye un idioma."
                )
                continue
            if language is not None:
                entries.append(LanguageEntry(language=language, level=level))
                if explicit_detail and level is None:
                    warnings.append(
                        f"languages[{len(entries) - 1}] no incluye un nivel."
                    )
                if (
                    explicit_detail
                    and level is not None
                    and LANGUAGE_LEVEL_PATTERN.fullmatch(level) is None
                ):
                    warnings.append(
                        f"languages[{len(entries) - 1}] contiene un nivel "
                        "no normalizado."
                    )

    return LanguageExtractionResult(entries=entries, warnings=warnings)


def extract_certifications(lines: list[str]) -> list[CertificationEntry]:
    """
    Extrae certificaciones manteniendo la interfaz publica original.

    Args:
        lines: Lineas de la seccion de certificaciones.

    Returns:
        Certificaciones detectadas en su orden de aparicion.
    """
    return extract_certifications_with_warnings(lines).entries


def extract_certifications_with_warnings(
    lines: list[str],
) -> CertificationExtractionResult:
    """
    Extrae `nombre | institucion | fecha` cuando la estructura es explicita.

    Si hay demasiados segmentos, conserva toda la linea como nombre.

    Args:
        lines: Lineas de la seccion de certificaciones.

    Returns:
        Entradas estructuradas y advertencias de ambiguedad.
    """
    entries: list[CertificationEntry] = []
    warnings: list[str] = []

    for line in clean_nonempty_lines(lines):
        cleaned_line = _clean_list_line(line)
        textual_parts, normalized_date, ambiguous = _parse_dated_parts(
            cleaned_line,
            allow_range=False,
        )
        if ambiguous:
            entries.append(CertificationEntry(name=cleaned_line))
            warnings.append(
                f"certifications[{len(entries) - 1}] tiene una estructura "
                "ambigua."
            )
            continue

        entries.append(
            CertificationEntry(
                name=textual_parts[0] if textual_parts else None,
                institution=(
                    textual_parts[1] if len(textual_parts) == 2 else None
                ),
                date=normalized_date,
            )
        )

    return CertificationExtractionResult(entries=entries, warnings=warnings)


def extract_courses(lines: list[str]) -> list[CourseEntry]:
    """
    Extrae cursos manteniendo la interfaz publica original.

    Args:
        lines: Lineas de la seccion de cursos.

    Returns:
        Cursos detectados en su orden de aparicion.
    """
    return extract_courses_with_warnings(lines).entries


def extract_courses_with_warnings(
    lines: list[str],
) -> CourseExtractionResult:
    """
    Extrae nombre, institucion y fechas de cursos con barras verticales.

    Los rangos actuales se representan mediante `status="in_progress"`.

    Args:
        lines: Lineas de la seccion de cursos.

    Returns:
        Entradas estructuradas y advertencias de ambiguedad.
    """
    entries: list[CourseEntry] = []
    warnings: list[str] = []

    for line in clean_nonempty_lines(lines):
        cleaned_line = _clean_list_line(line)
        textual_parts, date_value, ambiguous = _parse_dated_parts(
            cleaned_line,
            allow_range=True,
        )
        if ambiguous:
            entries.append(CourseEntry(name=cleaned_line))
            warnings.append(
                f"courses[{len(entries) - 1}] tiene una estructura ambigua."
            )
            continue

        date_range = find_date_range(cleaned_line)
        entries.append(
            CourseEntry(
                name=textual_parts[0] if textual_parts else None,
                institution=(
                    textual_parts[1] if len(textual_parts) == 2 else None
                ),
                start_date=(
                    date_range.start_date if date_range is not None else None
                ),
                end_date=(
                    date_range.end_date
                    if date_range is not None
                    else date_value
                ),
                status=(
                    "in_progress"
                    if date_range is not None and date_range.current
                    else None
                ),
            )
        )

    return CourseExtractionResult(entries=entries, warnings=warnings)


def extract_projects(lines: list[str]) -> list[ProjectEntry]:
    """
    Extrae proyectos manteniendo la interfaz publica original.

    Args:
        lines: Lineas de la seccion de proyectos.

    Returns:
        Proyectos detectados en su orden de aparicion.
    """
    return extract_projects_with_warnings(lines).entries


def extract_projects_with_warnings(
    lines: list[str],
) -> ProjectExtractionResult:
    """
    Agrupa bloques con etiquetas de nombre, descripcion, tecnologias y URL.

    Si la seccion no usa etiquetas, cada linea sigue siendo un proyecto
    independiente para conservar el comportamiento y el orden originales.

    Args:
        lines: Lineas de la seccion de proyectos.

    Returns:
        Entradas estructuradas y advertencias de ambiguedad.
    """
    cleaned_lines = [
        _clean_list_line(line) for line in clean_nonempty_lines(lines)
    ]
    if not cleaned_lines:
        return ProjectExtractionResult(entries=[], warnings=[])

    if not any(_split_project_field(line)[0] for line in cleaned_lines):
        return ProjectExtractionResult(
            entries=[
                ProjectEntry(name=line, description=line)
                for line in cleaned_lines
            ],
            warnings=[],
        )

    entries: list[ProjectEntry] = []
    warnings: list[str] = []
    current: dict[str, object] = {}

    for line in cleaned_lines:
        field_name, value = _split_project_field(line)
        if field_name == "name":
            _append_project(entries, current)
            current = {"name": value}
            continue

        if field_name is None:
            if current:
                _append_description(current, line)
            else:
                entries.append(ProjectEntry(name=line, description=line))
            continue

        if not current:
            current = {}
        if field_name == "technologies":
            technologies = current.setdefault("technologies", [])
            if isinstance(technologies, list):
                technologies.extend(split_values(value))
        elif field_name == "description":
            _append_description(current, value)
        elif field_name == "url":
            if current.get("url") is not None:
                warnings.append(
                    f"projects[{len(entries)}] contiene mas de una URL."
                )
                _append_description(current, line)
            else:
                current["url"] = value or None

    _append_project(entries, current)
    for index, entry in enumerate(entries):
        if entry.name is None:
            warnings.append(f"projects[{index}] no incluye un nombre explicito.")

    return ProjectExtractionResult(entries=entries, warnings=warnings)


def _clean_list_line(line: str) -> str:
    return strip_bullet(line) if is_bullet_line(line) else line.strip()


def _split_language_and_level(
    line: str,
) -> tuple[str | None, str | None, bool]:
    level_prefix = LANGUAGE_LEVEL_PREFIX_PATTERN.fullmatch(line)
    if level_prefix is not None:
        return (
            level_prefix.group("language").strip() or None,
            level_prefix.group("level").strip() or None,
            True,
        )

    if ":" in line:
        language, level = line.split(":", maxsplit=1)
        return language.strip() or None, level.strip() or None, True

    separated_values = DETAIL_SEPARATOR_PATTERN.split(line, maxsplit=1)
    if len(separated_values) == 2:
        return (
            separated_values[0].strip() or None,
            separated_values[1].strip() or None,
            True,
        )

    trailing_level = TRAILING_LANGUAGE_LEVEL_PATTERN.fullmatch(line)
    if trailing_level is not None:
        return (
            trailing_level.group("language").strip() or None,
            trailing_level.group("level").strip() or None,
            False,
        )

    parenthesized_level = PARENTHESIZED_LANGUAGE_LEVEL_PATTERN.fullmatch(line)
    if parenthesized_level is not None:
        return (
            parenthesized_level.group("language").strip() or None,
            parenthesized_level.group("level").strip() or None,
            True,
        )

    return line.strip() or None, None, False


def _split_language_items(line: str) -> list[str]:
    return [
        value.strip()
        for value in LANGUAGE_ENTRY_SEPARATOR_PATTERN.split(line)
        if value.strip()
    ]


def _parse_dated_parts(
    line: str,
    *,
    allow_range: bool,
) -> tuple[list[str], str | None, bool]:
    date_range = find_date_range(line) if allow_range else None
    single_date = find_single_date(line) if date_range is None else None
    raw_date = (
        date_range.raw
        if date_range is not None
        else single_date[0] if single_date is not None else None
    )
    normalized_date = (
        date_range.start_date
        if date_range is not None
        else single_date[1] if single_date is not None else None
    )
    text_without_date = (
        line.replace(raw_date, "", 1) if raw_date is not None else line
    ).strip(" |\u2013\u2014-")
    parts = [part.strip() for part in text_without_date.split("|") if part.strip()]
    return parts, normalized_date, len(parts) > 2 or not parts


def _split_project_field(line: str) -> tuple[str | None, str]:
    if ":" not in line:
        return None, line
    label, value = line.split(":", maxsplit=1)
    field_name = PROJECT_LABELS.get(_normalize_label(label))
    return (field_name, value.strip()) if field_name else (None, line)


def _normalize_label(value: str) -> str:
    return normalize_lookup_text(value)


def _append_description(project: dict[str, object], value: str) -> None:
    description = project.get("description")
    project["description"] = (
        f"{description}\n{value}" if isinstance(description, str) else value
    )


def _append_project(
    entries: list[ProjectEntry],
    project: dict[str, object],
) -> None:
    if not project:
        return
    technologies = project.get("technologies")
    entries.append(
        ProjectEntry(
            name=_optional_string(project.get("name")),
            description=_optional_string(project.get("description")),
            technologies=(
                deduplicate_preserving_order(technologies)
                if isinstance(technologies, list)
                else []
            ),
            url=_optional_string(project.get("url")),
        )
    )
    project.clear()


def _optional_string(value: object) -> str | None:
    return value if isinstance(value, str) and value else None
