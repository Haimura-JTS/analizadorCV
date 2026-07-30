"""
Extractor conservador de formacion academica.

Separa entradas mediante encabezados estructurados y fechas, e identifica
institucion y titulacion solo cuando sus terminos aportan evidencia suficiente.

No deduce estados de finalizacion ni completa instituciones ausentes.
"""

from dataclasses import asdict, dataclass
import re

from cv_analyzer.extraction_utils import clean_nonempty_lines, find_date_range
from cv_analyzer.extraction_utils import find_single_date
from cv_analyzer.extraction_utils import normalize_lookup_text


# Separa titulacion e institucion cuando existe un delimitador visible.
EDUCATION_HEADER_SEPARATOR_PATTERN = re.compile(
    r"\s+(?:\||@|-|\u2013|\u2014)\s+"
)

DEGREE_TERMS = {
    "bachelor",
    "bsc",
    "certificado",
    "degree",
    "diploma",
    "doctorado",
    "engineering",
    "formacion profesional",
    "grado",
    "ingenieria",
    "licenciatura",
    "master",
    "msc",
    "phd",
    "tecnico",
}
INSTITUTION_TERMS = {
    "academy",
    "colegio",
    "escuela",
    "facultad",
    "institute",
    "instituto",
    "school",
    "university",
    "universidad",
}


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


@dataclass(frozen=True)
class EducationExtractionResult:
    """Entradas academicas y advertencias de ambiguedad."""

    entries: list[EducationEntry]
    warnings: list[str]


def extract_education(lines: list[str]) -> list[EducationEntry]:
    """
    Extrae formacion manteniendo la interfaz publica original.

    Args:
        lines: Lineas de la seccion de formacion.

    Returns:
        Entradas detectadas en su orden de aparicion.
    """
    return extract_education_with_warnings(lines).entries


def extract_education_with_warnings(
    lines: list[str],
) -> EducationExtractionResult:
    """
    Extrae estudios y registra campos estructurales ambiguos.

    Args:
        lines: Lineas de la seccion de formacion.

    Returns:
        Entradas ordenadas y advertencias sin contenido personal.
    """
    cleaned_lines = clean_nonempty_lines(lines)
    if not cleaned_lines:
        return EducationExtractionResult(entries=[], warnings=[])

    groups = _group_education_lines(cleaned_lines)
    entries: list[EducationEntry] = []
    warnings: list[str] = []

    for index, group in enumerate(groups):
        entry = _parse_education_group(group)
        entries.append(entry)
        if entry.institution is None or entry.degree is None:
            warnings.append(
                f"education[{index}] no permite diferenciar institucion "
                "y titulacion."
            )

    return EducationExtractionResult(entries=entries, warnings=warnings)


def _group_education_lines(lines: list[str]) -> list[list[str]]:
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
    if any(_extract_header_fields(line)) and _group_has_header(current_group):
        return True

    if not any(_line_has_date(item) for item in current_group):
        return False

    lookahead = lines[index : index + 3]
    return any(_line_has_date(item) for item in lookahead)


def _group_has_header(lines: list[str]) -> bool:
    return any(any(_extract_header_fields(line)) for line in lines)


def _parse_education_group(lines: list[str]) -> EducationEntry:
    date_range = next(
        (
            extracted_range
            for line in lines
            if (extracted_range := find_date_range(line)) is not None
        ),
        None,
    )
    single_date = (
        None
        if date_range is not None
        else next(
            (
                extracted_date
                for line in lines
                if (extracted_date := find_single_date(line)) is not None
            ),
            None,
        )
    )
    institution, degree = _find_institution_and_degree(lines)

    return EducationEntry(
        institution=institution,
        degree=degree,
        start_date=date_range.start_date if date_range else None,
        end_date=(
            date_range.end_date
            if date_range
            else single_date[1] if single_date else None
        ),
        status="in_progress" if date_range and date_range.current else None,
        description="\n".join(lines),
    )


def _find_institution_and_degree(
    lines: list[str],
) -> tuple[str | None, str | None]:
    for line in lines:
        institution, degree = _extract_header_fields(line)
        if institution is not None or degree is not None:
            return institution, degree

    candidates = [line for line in lines if not _line_has_date(line)]
    if len(candidates) >= 2:
        return _infer_institution_and_degree(candidates[0], candidates[1])
    if len(candidates) == 1:
        if _contains_term(candidates[0], DEGREE_TERMS):
            return None, candidates[0]
        if _contains_term(candidates[0], INSTITUTION_TERMS):
            return candidates[0], None
    return None, None


def _extract_header_fields(line: str) -> tuple[str | None, str | None]:
    date_range = find_date_range(line)
    single_date = find_single_date(line) if date_range is None else None
    date_fragment = (
        date_range.raw
        if date_range is not None
        else single_date[0] if single_date else None
    )
    header_text = (
        line.replace(date_fragment, "", 1)
        if date_fragment is not None
        else line
    )
    header_text = header_text.strip(" |@-\u2013\u2014")
    parts = [
        part.strip()
        for part in EDUCATION_HEADER_SEPARATOR_PATTERN.split(header_text)
        if part.strip()
    ]
    if len(parts) != 2:
        return None, None
    return _infer_institution_and_degree(parts[0], parts[1])


def _infer_institution_and_degree(
    first_value: str,
    second_value: str,
) -> tuple[str | None, str | None]:
    first_is_degree = _contains_term(first_value, DEGREE_TERMS)
    second_is_degree = _contains_term(second_value, DEGREE_TERMS)
    first_is_institution = _contains_term(first_value, INSTITUTION_TERMS)
    second_is_institution = _contains_term(second_value, INSTITUTION_TERMS)

    if first_is_degree and second_is_institution:
        return second_value, first_value
    if second_is_degree and first_is_institution:
        return first_value, second_value
    return None, None


def _line_has_date(line: str) -> bool:
    return find_date_range(line) is not None or find_single_date(line) is not None


def _contains_term(value: str, terms: set[str]) -> bool:
    normalized_value = normalize_lookup_text(value)
    return any(term in normalized_value for term in terms)
