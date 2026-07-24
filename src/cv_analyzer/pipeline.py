"""
Pipeline principal del Analizador de CV.

Coordina lectura, limpieza, deteccion, extraccion, construccion y validacion.
Los detalles de cada operacion permanecen en sus modulos especializados.
"""

from datetime import datetime, timezone
import logging
from pathlib import Path

from cv_analyzer.additional_sections_extractor import (
    extract_certifications,
    extract_courses,
    extract_languages,
    extract_projects,
)
from cv_analyzer.constants import INVALID_RESULT_MESSAGE
from cv_analyzer.constants import UNEXPECTED_PROCESSING_ERROR_MESSAGE
from cv_analyzer.contact_extractor import extract_contact_info
from cv_analyzer.education_extractor import extract_education
from cv_analyzer.exceptions import CVAnalyzerError
from cv_analyzer.experience_extractor import extract_experience
from cv_analyzer.json_builder import build_failed_cv_result
from cv_analyzer.json_builder import build_structured_cv_result
from cv_analyzer.pdf_reader import PDFTextExtractionResult, read_pdf_text
from cv_analyzer.personal_extractor import extract_initial_personal_info
from cv_analyzer.section_detector import detect_sections_with_warnings
from cv_analyzer.skills_extractor import extract_skills
from cv_analyzer.text_cleaner import clean_text, split_clean_lines
from cv_analyzer.validators import validate_and_annotate_cv_result
from cv_analyzer.validators import validate_cv_result_schema


logger = logging.getLogger(__name__)


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
    source_file = _source_file_name(file_path)
    pdf_result: PDFTextExtractionResult | None = None
    logger.info("Iniciando procesamiento del CV: %s", source_file)

    try:
        path = Path(file_path)
        pdf_result = read_pdf_text(path)
        result = _process_extracted_pdf(path, pdf_result)
    except (CVAnalyzerError, OSError) as error:
        error_message = str(error).strip() or error.__class__.__name__
        logger.warning(
            "No se pudo procesar el CV %s: %s",
            source_file,
            error_message,
        )
        return _build_failure_result(
            source_file=source_file,
            errors=[error_message],
            pdf_result=pdf_result,
        )
    except Exception:
        logger.exception(
            "Fallo inesperado al procesar el CV %s.",
            source_file,
        )
        return _build_failure_result(
            source_file=source_file,
            errors=[UNEXPECTED_PROCESSING_ERROR_MESSAGE],
            pdf_result=pdf_result,
        )

    if _was_processed_successfully(result):
        logger.info(
            "CV procesado correctamente: %s (%s paginas).",
            source_file,
            pdf_result.page_count,
        )
    return result


def _process_extracted_pdf(
    file_path: Path,
    pdf_result: PDFTextExtractionResult,
) -> dict[str, object]:
    cleaned_text = clean_text(pdf_result.text)
    lines = split_clean_lines(cleaned_text)
    personal_info = extract_initial_personal_info(lines)
    contact_info = extract_contact_info(cleaned_text)
    section_result = detect_sections_with_warnings(lines)
    sections = section_result.sections
    processed_at = _utc_timestamp()

    result = build_structured_cv_result(
        full_name=personal_info.full_name,
        professional_title=personal_info.professional_title,
        contact=contact_info,
        education=extract_education(sections.get("education", [])),
        experience=extract_experience(sections.get("experience", [])),
        skills=extract_skills(sections.get("skills", [])),
        languages=extract_languages(sections.get("languages", [])),
        certifications=extract_certifications(
            sections.get("certifications", [])
        ),
        courses=extract_courses(sections.get("courses", [])),
        projects=extract_projects(sections.get("projects", [])),
        unclassified_text=sections.get("unclassified", []),
        warnings=[*pdf_result.warnings, *section_result.warnings],
        summary=_join_lines(sections.get("profile", [])),
        source_file=file_path.name,
        file_size_bytes=pdf_result.file_size_bytes,
        page_count=pdf_result.page_count,
        processed_at=processed_at,
    )
    validation_report = validate_and_annotate_cv_result(result)

    if validation_report.errors:
        logger.error(
            "El resultado de %s no cumple el esquema: %s",
            file_path.name,
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
            pdf_result.file_size_bytes if pdf_result is not None else None
        ),
        page_count=pdf_result.page_count if pdf_result is not None else None,
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


def _join_lines(lines: list[str]) -> str | None:
    joined_lines = "\n".join(line for line in lines if line.strip()).strip()
    return joined_lines or None


def _was_processed_successfully(result: dict[str, object]) -> bool:
    metadata = result.get("metadata")
    return (
        isinstance(metadata, dict)
        and metadata.get("processed_successfully") is True
    )


def _merge_unique_messages(messages: list[str]) -> list[str]:
    return list(dict.fromkeys(messages))


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()
