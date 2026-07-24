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
from cv_analyzer.date_normalizer import normalize_date, normalize_date_range
from cv_analyzer.models import CVResultModel


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
    date_warnings = normalize_cv_result_dates(annotated_data)
    warnings = _merge_unique_strings(
        date_warnings,
        collect_cv_warnings(annotated_data),
    )
    errors: list[str] = []

    try:
        validated_model = validate_cv_result_schema(annotated_data)
        annotated_data = validated_model.model_dump()
    except ValidationError as error:
        errors = [str(item["msg"]) for item in error.errors()]

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
            supports_current=section_name == "experience",
        )

    _normalize_certification_dates(data.get("certifications"), warnings)
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
            current = bool(entry.get("current"))
            if current and end_date is not None:
                warnings.append(
                    f"{section_name}[{index}] indica actualidad y fecha final."
                )
            if isinstance(start_date, str) and isinstance(end_date, str):
                if start_date > end_date:
                    warnings.append(
                        f"{section_name}[{index}] tiene fechas invertidas."
                    )


def _normalize_date_fields_in_entries(
    section: object,
    warnings: list[str],
    *,
    supports_current: bool,
) -> None:
    if not isinstance(section, list):
        return

    for entry in section:
        if not isinstance(entry, dict):
            continue

        start_date = entry.get("start_date")
        end_date = entry.get("end_date")
        if isinstance(start_date, str) and end_date is None:
            if DATE_RANGE_SEPARATOR_PATTERN.search(start_date):
                normalized_range = normalize_date_range(start_date)
                entry["start_date"] = normalized_range.start_date
                entry["end_date"] = normalized_range.end_date
                warnings.extend(normalized_range.warnings)
                if supports_current:
                    entry["current"] = normalized_range.current
                continue

        _normalize_single_date_field(entry, "start_date", warnings)
        _normalize_single_date_field(entry, "end_date", warnings)


def _normalize_certification_dates(
    section: object,
    warnings: list[str],
) -> None:
    if not isinstance(section, list):
        return

    for entry in section:
        if isinstance(entry, dict):
            _normalize_single_date_field(entry, "date", warnings)


def _normalize_single_date_field(
    entry: dict[str, object],
    field_name: str,
    warnings: list[str],
) -> None:
    value = entry.get(field_name)
    if not isinstance(value, str):
        return

    normalized_value = normalize_date(value)
    if normalized_value is None:
        warnings.append(f"Fecha ambigua en {field_name}: {value}.")
    entry[field_name] = normalized_value


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
