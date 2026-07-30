"""
Pipeline principal del Analizador de CV.

Coordina lectura, limpieza, deteccion, extraccion, construccion y validacion.
Los detalles de cada operacion permanecen en sus modulos especializados.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
import logging
from pathlib import Path

from cv_analyzer.additional_sections_extractor import (
    extract_certifications_with_warnings,
    extract_courses_with_warnings,
    extract_languages_with_warnings,
    extract_projects_with_warnings,
)
from cv_analyzer.constants import EXPECTED_PROCESSING_ERROR_MESSAGE
from cv_analyzer.constants import FILE_ACCESS_ERROR_MESSAGE
from cv_analyzer.constants import FILE_IS_DIRECTORY_MESSAGE
from cv_analyzer.constants import FILE_NOT_FOUND_MESSAGE
from cv_analyzer.constants import INVALID_RESULT_MESSAGE
from cv_analyzer.constants import UNEXPECTED_PROCESSING_ERROR_MESSAGE
from cv_analyzer.contact_extractor import extract_contact_info
from cv_analyzer.education_extractor import extract_education_with_warnings
from cv_analyzer.exceptions import CVAnalyzerError
from cv_analyzer.experience_extractor import extract_experience_with_warnings
from cv_analyzer.json_builder import build_failed_cv_result
from cv_analyzer.json_builder import build_structured_cv_result
from cv_analyzer.pdf_reader import PDFTextExtractionResult, read_pdf_text
from cv_analyzer.personal_extractor import extract_initial_personal_info
from cv_analyzer.section_detector import detect_sections_with_warnings
from cv_analyzer.skills_extractor import extract_skills_with_warnings
from cv_analyzer.text_cleaner import clean_text, split_clean_lines
from cv_analyzer.validators import validate_and_annotate_cv_result
from cv_analyzer.validators import validate_cv_result_schema


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CVProcessingOutput:
    """
    Resultado del pipeline para consumidores que necesitan texto y JSON.

    Args:
        data: Resultado estructurado que cumple el contrato del proyecto.
        extracted_text: Texto original extraido o None si la lectura fallo.
    """

    data: dict[str, object]
    extracted_text: str | None


def process_cv_file(file_path: str | Path) -> dict[str, object]:
    """
    Procesa un archivo PDF y devuelve siempre el contrato JSON del proyecto.

    Los errores esperados de archivo se convierten en una salida con
    `processed_successfully` igual a False. Los fallos inesperados se registran
    con su traza y se exponen mediante un mensaje generico.

    Args:
        file_path: Ruta del curriculum en formato PDF.

    Returns:
        Resultado completo y serializable del procesamiento.
    """
    return process_cv_file_with_details(file_path).data


def process_cv_file_with_details(
    file_path: str | Path,
) -> CVProcessingOutput:
    """
    Procesa un PDF y conserva el texto para clientes de presentacion.

    Esta variante evita que una interfaz tenga que leer el documento por
    segunda vez. Mantiene el mismo manejo de errores que `process_cv_file()`.

    Args:
        file_path: Ruta del curriculum en formato PDF.

    Returns:
        Resultado estructurado junto con el texto extraido disponible.
    """
    source_file = _source_file_name(file_path)
    pdf_result: PDFTextExtractionResult | None = None
    logger.info("Iniciando procesamiento de un CV.")

    try:
        path = Path(file_path)
        pdf_result = read_pdf_text(path)
        result = _process_extracted_pdf(path, pdf_result)
    except CVAnalyzerError as error:
        error_message = _public_domain_error_message(error)
        logger.warning(
            "Procesamiento rechazado por un error esperado (%s).",
            error.__class__.__name__,
        )
        return CVProcessingOutput(
            data=_build_failure_result(
                source_file=source_file,
                errors=[error_message],
                pdf_result=pdf_result,
            ),
            extracted_text=_extracted_text(pdf_result),
        )
    except OSError as error:
        logger.warning(
            "No se pudo acceder al PDF (%s).",
            error.__class__.__name__,
        )
        return CVProcessingOutput(
            data=_build_failure_result(
                source_file=source_file,
                errors=[_public_os_error_message(error)],
                pdf_result=pdf_result,
            ),
            extracted_text=_extracted_text(pdf_result),
        )
    except Exception:
        logger.exception("Fallo inesperado durante el procesamiento del CV.")
        return CVProcessingOutput(
            data=_build_failure_result(
                source_file=source_file,
                errors=[UNEXPECTED_PROCESSING_ERROR_MESSAGE],
                pdf_result=pdf_result,
            ),
            extracted_text=_extracted_text(pdf_result),
        )

    if _was_processed_successfully(result):
        logger.info(
            "CV procesado correctamente (%s paginas).",
            pdf_result.page_count,
        )
    return CVProcessingOutput(
        data=result,
        extracted_text=pdf_result.text,
    )


def _process_extracted_pdf(
    file_path: Path,
    pdf_result: PDFTextExtractionResult,
) -> dict[str, object]:
    cleaned_text = clean_text(pdf_result.text)
    lines = split_clean_lines(cleaned_text)
    personal_info = extract_initial_personal_info(lines)
    contact_info = extract_contact_info(
        "\n".join([cleaned_text, *pdf_result.embedded_links])
    )
    section_result = detect_sections_with_warnings(lines)
    sections = section_result.sections
    education_result = extract_education_with_warnings(
        sections.get("education", [])
    )
    experience_result = extract_experience_with_warnings(
        sections.get("experience", [])
    )
    skills_result = extract_skills_with_warnings(
        sections.get("skills", [])
    )
    language_result = extract_languages_with_warnings(
        sections.get("languages", [])
    )
    certification_result = extract_certifications_with_warnings(
        sections.get("certifications", [])
    )
    course_result = extract_courses_with_warnings(
        sections.get("courses", [])
    )
    project_result = extract_projects_with_warnings(
        sections.get("projects", [])
    )
    processed_at = _utc_timestamp()

    result = build_structured_cv_result(
        full_name=personal_info.full_name,
        professional_title=personal_info.professional_title,
        contact=contact_info,
        education=education_result.entries,
        experience=experience_result.entries,
        skills=skills_result.skills,
        languages=language_result.entries,
        certifications=certification_result.entries,
        courses=course_result.entries,
        projects=project_result.entries,
        unclassified_text=sections.get("unclassified", []),
        warnings=_merge_unique_messages(
            [
                *pdf_result.warnings,
                *section_result.warnings,
                *education_result.warnings,
                *experience_result.warnings,
                *skills_result.warnings,
                *language_result.warnings,
                *certification_result.warnings,
                *course_result.warnings,
                *project_result.warnings,
            ]
        ),
        summary=_join_lines(sections.get("profile", [])),
        source_file=file_path.name,
        file_size_bytes=pdf_result.file_size_bytes,
        page_count=pdf_result.page_count,
        processed_at=processed_at,
    )
    validation_report = validate_and_annotate_cv_result(result)

    if validation_report.errors:
        logger.error(
            "El resultado intermedio no cumple el esquema: %s",
            "; ".join(validation_report.errors),
        )
        return _build_failure_result(
            source_file=file_path.name,
            errors=[INVALID_RESULT_MESSAGE, *validation_report.errors],
            pdf_result=pdf_result,
            warnings=validation_report.warnings,
            processed_at=processed_at,
        )

    return validation_report.data


def _build_failure_result(
    *,
    source_file: str | None,
    errors: list[str],
    pdf_result: PDFTextExtractionResult | None,
    warnings: list[str] | None = None,
    processed_at: str | None = None,
) -> dict[str, object]:
    result = build_failed_cv_result(
        source_file=source_file,
        errors=errors,
        processed_at=processed_at or _utc_timestamp(),
        file_size_bytes=(
            _non_negative_int(pdf_result.file_size_bytes)
            if pdf_result is not None
            else None
        ),
        page_count=(
            _non_negative_int(pdf_result.page_count)
            if pdf_result is not None
            else None
        ),
        warnings=_merge_unique_messages(
            [
                *(pdf_result.warnings if pdf_result is not None else []),
                *(warnings or []),
            ]
        ),
    )
    return validate_cv_result_schema(result).model_dump()


def _source_file_name(file_path: str | Path) -> str | None:
    try:
        path = Path(file_path)
    except (TypeError, ValueError):
        return None

    return path.name or str(path) or None


def _public_domain_error_message(error: CVAnalyzerError) -> str:
    message = str(error).strip()
    return message or EXPECTED_PROCESSING_ERROR_MESSAGE


def _public_os_error_message(error: OSError) -> str:
    if isinstance(error, FileNotFoundError):
        return FILE_NOT_FOUND_MESSAGE
    if isinstance(error, IsADirectoryError):
        return FILE_IS_DIRECTORY_MESSAGE
    return FILE_ACCESS_ERROR_MESSAGE


def _join_lines(lines: list[str]) -> str | None:
    joined_lines = "\n".join(line for line in lines if line.strip()).strip()
    return joined_lines or None


def _was_processed_successfully(result: dict[str, object]) -> bool:
    metadata = result.get("metadata")
    return (
        isinstance(metadata, dict)
        and metadata.get("processed_successfully") is True
    )


def _extracted_text(
    pdf_result: PDFTextExtractionResult | None,
) -> str | None:
    return pdf_result.text if pdf_result is not None else None


def _merge_unique_messages(messages: list[object]) -> list[str]:
    unique_messages: list[str] = []
    seen_messages: set[str] = set()

    for message in messages:
        if not isinstance(message, str):
            continue
        cleaned_message = message.strip()
        if not cleaned_message or cleaned_message in seen_messages:
            continue
        seen_messages.add(cleaned_message)
        unique_messages.append(cleaned_message)

    return unique_messages


def _non_negative_int(value: object) -> int | None:
    if type(value) is not int or value < 0:
        return None
    return value


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()
