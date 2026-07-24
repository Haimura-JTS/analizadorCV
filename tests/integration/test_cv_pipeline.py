from datetime import datetime
import logging
from pathlib import Path

import pytest

import cv_analyzer.pipeline as pipeline_module
from cv_analyzer.constants import INVALID_RESULT_MESSAGE
from cv_analyzer.constants import UNEXPECTED_PROCESSING_ERROR_MESSAGE
from cv_analyzer.exceptions import InvalidFileTypeError
from cv_analyzer.models import CVResultModel
from cv_analyzer.pdf_reader import PDFTextExtractionResult
from cv_analyzer.pipeline import process_cv_file
from cv_analyzer.pipeline import process_cv_file_with_details


CV_TEXT = """\
Ana Garcia
Backend Developer
ana@example.com
PERFIL
Desarrolladora de servicios web.
EXPERIENCIA
Acme - Backend Developer
- Desarrollo de APIs
FORMACION
Grado en Ingenieria Informatica
HABILIDADES
Python, FastAPI, PostgreSQL
IDIOMAS
Ingles - C1
CERTIFICACIONES
Python Professional
CURSOS
Arquitectura de software
PROYECTOS
Analizador de CV
"""


def _pdf_result() -> PDFTextExtractionResult:
    return PDFTextExtractionResult(
        text=CV_TEXT,
        page_count=2,
        file_size_bytes=2048,
        warnings=[],
    )


def test_process_cv_file_connects_the_complete_flow(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        pipeline_module,
        "read_pdf_text",
        lambda _: _pdf_result(),
    )

    output = process_cv_file_with_details(Path("ana-garcia.pdf"))
    result = output.data

    CVResultModel.model_validate(result)
    assert output.extracted_text == CV_TEXT
    assert result["personal_data"]["full_name"] == "Ana Garcia"
    assert result["personal_data"]["professional_title"] == (
        "Backend Developer"
    )
    assert result["personal_data"]["summary"] == (
        "Desarrolladora de servicios web."
    )
    assert result["contact"]["email"] == "ana@example.com"
    assert result["experience"][0]["responsibilities"] == [
        "Desarrollo de APIs"
    ]
    assert result["education"][0]["description"] == (
        "Grado en Ingenieria Informatica"
    )
    assert result["skills"]["technical"] == [
        "Python",
        "FastAPI",
        "PostgreSQL",
    ]
    assert result["languages"][0] == {
        "language": "Ingles",
        "level": "C1",
    }
    assert result["metadata"]["source_file"] == "ana-garcia.pdf"
    assert result["metadata"]["page_count"] == 2
    assert result["metadata"]["file_size_bytes"] == 2048
    assert result["metadata"]["processed_successfully"] is True

    processed_at = datetime.fromisoformat(result["metadata"]["processed_at"])
    assert processed_at.tzinfo is not None


def test_process_cv_file_returns_valid_json_for_expected_error(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    def raise_invalid_file(_: Path) -> PDFTextExtractionResult:
        raise InvalidFileTypeError("El archivo debe tener extension PDF.")

    monkeypatch.setattr(
        pipeline_module,
        "read_pdf_text",
        raise_invalid_file,
    )

    with caplog.at_level(logging.WARNING, logger="cv_analyzer.pipeline"):
        result = process_cv_file("curriculum.txt")

    CVResultModel.model_validate(result)
    assert result["metadata"]["source_file"] == "curriculum.txt"
    assert result["metadata"]["processed_successfully"] is False
    assert result["metadata"]["errors"] == [
        "El archivo debe tener extension PDF."
    ]
    assert "No se pudo procesar el CV curriculum.txt" in caplog.text


def test_process_cv_file_hides_unexpected_error_details(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    def raise_unexpected_error(_: Path) -> PDFTextExtractionResult:
        raise RuntimeError("detalle tecnico sensible")

    monkeypatch.setattr(
        pipeline_module,
        "read_pdf_text",
        raise_unexpected_error,
    )

    with caplog.at_level(logging.ERROR, logger="cv_analyzer.pipeline"):
        result = process_cv_file("curriculum.pdf")

    CVResultModel.model_validate(result)
    assert result["metadata"]["processed_successfully"] is False
    assert result["metadata"]["errors"] == [
        UNEXPECTED_PROCESSING_ERROR_MESSAGE
    ]
    assert "detalle tecnico sensible" not in result["metadata"]["errors"][0]
    assert "Fallo inesperado al procesar" in caplog.text


def test_process_cv_file_replaces_invalid_intermediate_result(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    monkeypatch.setattr(
        pipeline_module,
        "read_pdf_text",
        lambda _: _pdf_result(),
    )
    monkeypatch.setattr(
        pipeline_module,
        "extract_skills",
        lambda _: {"unknown_category": ["Python"]},
    )

    with caplog.at_level(logging.INFO, logger="cv_analyzer.pipeline"):
        result = process_cv_file("curriculum.pdf")

    CVResultModel.model_validate(result)
    assert result["metadata"]["processed_successfully"] is False
    assert result["metadata"]["page_count"] == 2
    assert result["metadata"]["errors"][0] == INVALID_RESULT_MESSAGE
    assert "CV procesado correctamente" not in caplog.text
