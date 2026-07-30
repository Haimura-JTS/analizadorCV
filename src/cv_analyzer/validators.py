"""
Modulo encargado de validar resultados estructurados del Analizador de CV.

Utiliza Pydantic para comprobar el contrato JSON y genera advertencias
comprensibles sobre campos ausentes o inconsistencias simples.

No extrae informacion nueva ni modifica datos personales fuera del resultado.
"""

from copy import deepcopy
from dataclasses import dataclass

from pydantic import ValidationError

from cv_analyzer.date_normalizer import DATE_RANGE_SEPARATOR_PATTERN
from cv_analyzer.date_normalizer import is_current_date
from cv_analyzer.date_normalizer import is_date_range_inverted
from cv_analyzer.date_normalizer import normalize_date, normalize_date_range
from cv_analyzer.models import CVResultModel


DEDUPLICATED_SKILL_FIELDS = (
    "technical",
    "tools",
    "programming_languages",
    "soft_skills",
)

VALIDATION_ERROR_MESSAGES = {
    "bool_type": "se esperaba un valor booleano.",
    "dict_type": "se esperaba un objeto.",
    "extra_forbidden": "campo no permitido por el contrato.",
    "greater_than_equal": "el valor debe ser mayor o igual que cero.",
    "int_type": "se esperaba un numero entero.",
    "list_type": "se esperaba una lista.",
    "string_pattern_mismatch": "el valor no cumple el formato requerido.",
    "string_type": "se esperaba texto.",
}


@dataclass(frozen=True)
class CVValidationReport:
    """
    Resultado de revisar un CV estructurado.

    Args:
        data: Resultado validado y anotado.
        warnings: Advertencias no bloqueantes.
        errors: Errores de esquema o consistencia.
    """

    data: dict[str, object]
    warnings: list[str]
    errors: list[str]


def validate_cv_result_schema(data: dict[str, object]) -> CVResultModel:
    """
    Valida el resultado contra el esquema Pydantic.

    Args:
        data: Diccionario generado por el analizador.

    Returns:
        Modelo Pydantic validado.

    Raises:
        ValidationError: Si el resultado no cumple el contrato.
    """
    return CVResultModel.model_validate(data)


def validate_and_annotate_cv_result(
    data: dict[str, object],
) -> CVValidationReport:
    """
    Valida un resultado y copia advertencias/errores en `metadata`.

    Args:
        data: Resultado estructurado del curriculum.

    Returns:
        Informe con datos anotados, advertencias y errores.
    """
    annotated_data = deepcopy(data)
    duplicate_warnings = deduplicate_cv_result_lists(annotated_data)
    date_warnings = normalize_cv_result_dates(annotated_data)
    warnings = _merge_unique_strings(
        duplicate_warnings,
        date_warnings,
        collect_cv_warnings(annotated_data),
    )
    errors: list[str] = []
    _prepare_existing_processing_state(annotated_data)

    try:
        validated_model = validate_cv_result_schema(annotated_data)
        annotated_data = validated_model.model_dump()
    except ValidationError as error:
        errors = _format_validation_errors(error)

    metadata = _ensure_metadata(annotated_data)
    metadata["warnings"] = _merge_unique_strings(
        _as_string_list(metadata.get("warnings")),
        warnings,
    )
    metadata["errors"] = _merge_unique_strings(
        _as_string_list(metadata.get("errors")),
        errors,
    )
    metadata["processed_successfully"] = not _as_string_list(
        metadata["errors"]
    )

    return CVValidationReport(
        data=annotated_data,
        warnings=_as_string_list(metadata["warnings"]),
        errors=_as_string_list(metadata["errors"]),
    )


def collect_cv_warnings(data: dict[str, object]) -> list[str]:
    """
    Recopila advertencias no bloqueantes sobre el resultado.

    Args:
        data: Resultado estructurado del curriculum.

    Returns:
        Lista de advertencias.
    """
    warnings: list[str] = []
    contact = data.get("contact")

    if isinstance(contact, dict) and not any(contact.values()):
        warnings.append("No se detectaron datos de contacto.")

    if not data.get("experience"):
        warnings.append("No se detecto experiencia profesional.")

    if not data.get("education"):
        warnings.append("No se detecto formacion academica.")

    _add_date_consistency_warnings(data, warnings)
    return warnings


def normalize_cv_result_dates(data: dict[str, object]) -> list[str]:
    """
    Normaliza fechas dentro de un resultado de CV ya construido.

    Args:
        data: Resultado estructurado que puede contener fechas parciales.

    Returns:
        Advertencias generadas durante la normalizacion.
    """
    warnings: list[str] = []
    for section_name in ("experience", "education", "courses"):
        _normalize_date_fields_in_entries(
            data.get(section_name),
            warnings,
            section_name=section_name,
        )

    _normalize_certification_dates(data.get("certifications"), warnings)
    return warnings


def deduplicate_cv_result_lists(data: dict[str, object]) -> list[str]:
    """
    Elimina duplicados seguros sin modificar listas de entradas completas.

    Se deduplican valores escalares repetidos dentro de habilidades, vinetas,
    tecnologias y mensajes. No se deduplican experiencias, estudios, idiomas
    ni texto no clasificado porque una repeticion puede ser significativa.

    Args:
        data: Resultado del CV que se revisara in situ.

    Returns:
        Advertencias para cada lista en la que se retiro contenido repetido.
    """
    warnings: list[str] = []
    skills = data.get("skills")
    if isinstance(skills, dict):
        for field_name in DEDUPLICATED_SKILL_FIELDS:
            _deduplicate_list_field(
                skills,
                field_name,
                f"skills.{field_name}",
                warnings,
            )

    _deduplicate_entry_fields(
        data.get("experience"),
        ("responsibilities", "achievements"),
        "experience",
        warnings,
    )
    _deduplicate_entry_fields(
        data.get("projects"),
        ("technologies",),
        "projects",
        warnings,
    )

    metadata = data.get("metadata")
    if isinstance(metadata, dict):
        for field_name in ("warnings", "errors"):
            _deduplicate_list_field(
                metadata,
                field_name,
                f"metadata.{field_name}",
                warnings,
            )

    return warnings


def _add_date_consistency_warnings(
    data: dict[str, object],
    warnings: list[str],
) -> None:
    for section_name in ("experience", "education", "courses"):
        section = data.get(section_name)
        if not isinstance(section, list):
            continue

        for index, entry in enumerate(section):
            if not isinstance(entry, dict):
                continue

            start_date = entry.get("start_date")
            end_date = entry.get("end_date")
            current = entry.get("current") is True
            in_progress = entry.get("status") == "in_progress"
            if (current or in_progress) and end_date is not None:
                warnings.append(
                    f"{section_name}[{index}] indica actualidad y fecha final."
                )
            if isinstance(start_date, str) and isinstance(end_date, str):
                if is_date_range_inverted(start_date, end_date):
                    warnings.append(
                        f"{section_name}[{index}] tiene fechas invertidas."
                    )


def _normalize_date_fields_in_entries(
    section: object,
    warnings: list[str],
    *,
    section_name: str,
) -> None:
    if not isinstance(section, list):
        return

    for index, entry in enumerate(section):
        if not isinstance(entry, dict):
            continue

        entry_path = f"{section_name}[{index}]"
        start_date = entry.get("start_date")
        end_date = entry.get("end_date")
        if isinstance(start_date, str) and end_date is None:
            if DATE_RANGE_SEPARATOR_PATTERN.search(start_date):
                normalized_range = normalize_date_range(start_date)
                entry["start_date"] = normalized_range.start_date
                entry["end_date"] = normalized_range.end_date
                warnings.extend(
                    f"{entry_path}.start_date: {warning}"
                    for warning in normalized_range.warnings
                )
                _mark_current_entry(
                    entry,
                    section_name=section_name,
                    current=normalized_range.current,
                )
                continue

        _normalize_single_date_field(
            entry,
            "start_date",
            warnings,
            entry_path=entry_path,
        )
        if isinstance(end_date, str) and is_current_date(end_date):
            entry["end_date"] = None
            _mark_current_entry(
                entry,
                section_name=section_name,
                current=True,
            )
        else:
            _normalize_single_date_field(
                entry,
                "end_date",
                warnings,
                entry_path=entry_path,
            )


def _normalize_certification_dates(
    section: object,
    warnings: list[str],
) -> None:
    if not isinstance(section, list):
        return

    for index, entry in enumerate(section):
        if isinstance(entry, dict):
            _normalize_single_date_field(
                entry,
                "date",
                warnings,
                entry_path=f"certifications[{index}]",
            )


def _normalize_single_date_field(
    entry: dict[str, object],
    field_name: str,
    warnings: list[str],
    *,
    entry_path: str,
) -> None:
    value = entry.get(field_name)
    if not isinstance(value, str):
        return

    normalized_value = normalize_date(value)
    if normalized_value is None:
        warnings.append(
            f"{entry_path}.{field_name} contiene una fecha ambigua: {value}."
        )
    entry[field_name] = normalized_value


def _mark_current_entry(
    entry: dict[str, object],
    *,
    section_name: str,
    current: bool,
) -> None:
    if not current:
        return
    if section_name == "experience":
        entry["current"] = True
    else:
        entry["status"] = "in_progress"


def _deduplicate_entry_fields(
    section: object,
    field_names: tuple[str, ...],
    section_name: str,
    warnings: list[str],
) -> None:
    if not isinstance(section, list):
        return

    for index, entry in enumerate(section):
        if not isinstance(entry, dict):
            continue
        for field_name in field_names:
            _deduplicate_list_field(
                entry,
                field_name,
                f"{section_name}[{index}].{field_name}",
                warnings,
            )


def _deduplicate_list_field(
    container: dict[str, object],
    field_name: str,
    field_path: str,
    warnings: list[str],
) -> None:
    values = container.get(field_name)
    if not isinstance(values, list):
        return

    unique_values: list[object] = []
    seen_values: set[str] = set()
    removed_duplicate = False

    for value in values:
        if not isinstance(value, str):
            unique_values.append(value)
            continue

        normalized_value = value.casefold()
        if normalized_value in seen_values:
            removed_duplicate = True
            continue
        seen_values.add(normalized_value)
        unique_values.append(value)

    if removed_duplicate:
        container[field_name] = unique_values
        warnings.append(f"Se eliminaron duplicados de {field_path}.")


def _prepare_existing_processing_state(data: dict[str, object]) -> None:
    metadata = data.get("metadata")
    if not isinstance(metadata, dict):
        return
    if _as_string_list(metadata.get("errors")):
        metadata["processed_successfully"] = False


def _format_validation_errors(error: ValidationError) -> list[str]:
    formatted_errors: list[str] = []
    for item in error.errors():
        location = ".".join(str(part) for part in item["loc"]) or "resultado"
        message = VALIDATION_ERROR_MESSAGES.get(
            str(item["type"]),
            str(item["msg"]),
        )
        formatted_errors.append(f"{location}: {message}")
    return formatted_errors


def _ensure_metadata(data: dict[str, object]) -> dict[str, object]:
    metadata = data.setdefault("metadata", {})
    if isinstance(metadata, dict):
        return metadata
    empty_metadata: dict[str, object] = {}
    data["metadata"] = empty_metadata
    return empty_metadata


def _as_string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def _merge_unique_strings(*groups: list[str]) -> list[str]:
    merged: list[str] = []
    seen_values: set[str] = set()

    for group in groups:
        for item in group:
            if item in seen_values:
                continue
            seen_values.add(item)
            merged.append(item)

    return merged
