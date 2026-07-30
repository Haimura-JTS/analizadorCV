"""
Extractor conservador de experiencia profesional.

Separa entradas mediante encabezados estructurados y rangos de fecha,
diferencia empresa y puesto cuando un termino profesional aporta evidencia y
clasifica vinetas como responsabilidades o logros.

No calcula duraciones ni completa empresas, puestos o fechas ambiguas.
"""

from dataclasses import asdict, dataclass
import re

from cv_analyzer.extraction_utils import clean_nonempty_lines, find_date_range
from cv_analyzer.extraction_utils import is_bullet_line, strip_bullet
from cv_analyzer.extraction_utils import normalize_lookup_text


# Separa encabezados como `Empresa - Puesto`, `Puesto | Empresa` o
# `Puesto @ Empresa`. Exige espacios para no dividir nombres con guion.
HEADER_SEPARATOR_PATTERN = re.compile(
    r"\s+(?:\||@|-|\u2013|\u2014)\s+"
)

# Terminos que permiten distinguir un puesto de una empresa. La lista es
# deliberadamente limitada; si ambos lados son ambiguos no se elige.
POSITION_TERMS = {
    "administrator",
    "administrador",
    "analista",
    "analyst",
    "architect",
    "arquitecto",
    "assistant",
    "consultant",
    "consultor",
    "coordinator",
    "coordinador",
    "developer",
    "desarrollador",
    "designer",
    "director",
    "engineer",
    "especialista",
    "gerente",
    "ingeniero",
    "lead",
    "manager",
    "scientist",
    "specialist",
    "supervisor",
    "tecnico",
    "technician",
}

# Una vineta se considera logro cuando contiene un verbo de resultado o una
# medida cuantificada. No intenta comprender el significado completo.
ACHIEVEMENT_PATTERN = re.compile(
    r"(?:\b(?:aument|ahorr|boost|grew|improv|increment|logr|mejor|"
    r"reduc|saved)\w*\b|\b\d+(?:[.,]\d+)?%|\b\d+[kKmM]\b)",
    re.IGNORECASE,
)


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


@dataclass(frozen=True)
class ExperienceExtractionResult:
    """Entradas de experiencia y advertencias de ambiguedad."""

    entries: list[ExperienceEntry]
    warnings: list[str]


def extract_experience(lines: list[str]) -> list[ExperienceEntry]:
    """
    Extrae experiencias manteniendo la interfaz publica original.

    Args:
        lines: Lineas de la seccion de experiencia.

    Returns:
        Entradas detectadas en su orden de aparicion.
    """
    return extract_experience_with_warnings(lines).entries


def extract_experience_with_warnings(
    lines: list[str],
) -> ExperienceExtractionResult:
    """
    Extrae experiencias y registra campos estructurales ambiguos.

    Args:
        lines: Lineas de la seccion de experiencia.

    Returns:
        Entradas ordenadas y advertencias sin contenido personal.
    """
    cleaned_lines = clean_nonempty_lines(lines)
    if not cleaned_lines:
        return ExperienceExtractionResult(entries=[], warnings=[])

    groups = _group_experience_lines(cleaned_lines)
    entries: list[ExperienceEntry] = []
    warnings: list[str] = []

    for index, group in enumerate(groups):
        entry = _parse_experience_group(group)
        entries.append(entry)
        if entry.company is None or entry.position is None:
            warnings.append(
                f"experience[{index}] no permite diferenciar empresa y puesto."
            )

    return ExperienceExtractionResult(entries=entries, warnings=warnings)


def _group_experience_lines(lines: list[str]) -> list[list[str]]:
    groups: list[list[str]] = []
    current_group: list[str] = []

    for index, line in enumerate(lines):
        if current_group and _starts_new_entry(
            lines,
            index=index,
            current_group=current_group,
        ):
            groups.append(current_group)
            current_group = []
        current_group.append(line)

    if current_group:
        groups.append(current_group)
    return groups


def _starts_new_entry(
    lines: list[str],
    *,
    index: int,
    current_group: list[str],
) -> bool:
    line = lines[index]
    if is_bullet_line(line):
        return False

    header_fields = _extract_header_fields(line)
    if any(header_fields) and (
        _group_has_structured_header(current_group)
        or any(is_bullet_line(item) for item in current_group)
    ):
        return True

    if not any(find_date_range(item) for item in current_group):
        return False

    lookahead = lines[index : index + 3]
    return any(find_date_range(item) is not None for item in lookahead)


def _group_has_structured_header(lines: list[str]) -> bool:
    return any(any(_extract_header_fields(line)) for line in lines)


def _parse_experience_group(lines: list[str]) -> ExperienceEntry:
    date_range = next(
        (
            extracted_range
            for line in lines
            if (extracted_range := find_date_range(line)) is not None
        ),
        None,
    )
    company, position = _find_company_and_position(lines)
    bullet_values = [
        strip_bullet(line) for line in lines if is_bullet_line(line)
    ]
    achievements = [
        value for value in bullet_values if ACHIEVEMENT_PATTERN.search(value)
    ]
    responsibilities = [
        value for value in bullet_values if value not in achievements
    ]

    return ExperienceEntry(
        company=company,
        position=position,
        start_date=date_range.start_date if date_range else None,
        end_date=date_range.end_date if date_range else None,
        current=date_range.current if date_range else False,
        description="\n".join(lines),
        responsibilities=responsibilities,
        achievements=achievements,
    )


def _find_company_and_position(
    lines: list[str],
) -> tuple[str | None, str | None]:
    for line in lines:
        if is_bullet_line(line):
            continue
        company, position = _extract_header_fields(line)
        if company is not None or position is not None:
            return company, position

    candidates = [
        line
        for line in lines
        if not is_bullet_line(line) and find_date_range(line) is None
    ]
    if len(candidates) >= 2:
        return _infer_company_and_position(candidates[0], candidates[1])
    if len(candidates) == 1 and _contains_position_term(candidates[0]):
        return None, candidates[0]
    return None, None


def _extract_header_fields(line: str) -> tuple[str | None, str | None]:
    date_range = find_date_range(line)
    header_text = (
        line.replace(date_range.raw, "", 1) if date_range is not None else line
    )
    header_text = header_text.strip(" |@-\u2013\u2014")
    parts = [
        part.strip()
        for part in HEADER_SEPARATOR_PATTERN.split(header_text)
        if part.strip()
    ]
    if len(parts) != 2:
        return None, None
    return _infer_company_and_position(parts[0], parts[1])


def _infer_company_and_position(
    first_value: str,
    second_value: str,
) -> tuple[str | None, str | None]:
    first_is_position = _contains_position_term(first_value)
    second_is_position = _contains_position_term(second_value)

    if first_is_position and not second_is_position:
        return second_value, first_value
    if second_is_position and not first_is_position:
        return first_value, second_value
    return None, None


def _contains_position_term(value: str) -> bool:
    words = {
        word.strip(".,:;()[]{}")
        for word in normalize_lookup_text(value).split()
    }
    return bool(words & POSITION_TERMS)
