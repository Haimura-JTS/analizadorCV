import json
from pathlib import Path

from cv_analyzer.constants import PDF_EMPTY_TEXT_MESSAGE, PDF_PROTECTED_MESSAGE
from cv_analyzer.models import CVResultModel
from cv_analyzer.pipeline import process_cv_file, process_cv_file_with_details
from tests.fixtures.cv_samples import (
    DUPLICATE_SECTION_CV_PAGES,
    ENGLISH_CV_PAGES,
    HEADERLESS_CV_PAGES,
    SPANISH_CV_PAGES,
)
from tests.fixtures.pdf_factory import (
    create_blank_pdf,
    create_encrypted_pdf,
    create_text_pdf,
)


def _assert_valid_json_result(result: dict[str, object]) -> None:
    CVResultModel.model_validate(result)
    json.dumps(result, ensure_ascii=True)


def test_real_spanish_pdf_runs_through_the_complete_pipeline(
    tmp_path: Path,
) -> None:
    file_path = create_text_pdf(
        tmp_path / "cv-espanol.pdf",
        SPANISH_CV_PAGES,
    )

    output = process_cv_file_with_details(file_path)
    result = output.data

    _assert_valid_json_result(result)
    assert output.extracted_text is not None
    assert "Desarrollo de APIs en Python" in output.extracted_text
    assert result["personal_data"]["full_name"] == "Alex Rivera"
    assert result["personal_data"]["professional_title"] == "Backend Developer"
    assert result["personal_data"]["summary"] == (
        "Desarrollador de servicios web y automatizaciones."
    )
    assert result["contact"] == {
        "email": "alex.rivera@example.test",
        "phone": "+34 612 345 678",
        "linkedin": "https://linkedin.com/in/alex-rivera",
        "github": "https://github.com/alex-rivera",
        "portfolio": "https://alexrivera.dev",
    }
    assert result["experience"][0]["responsibilities"] == [
        "Desarrollo de APIs en Python"
    ]
    assert "Northwind Labs - Backend Developer" in (
        result["experience"][0]["description"]
    )
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
    assert result["certifications"][0]["name"] == "Python Professional"
    assert result["courses"][0]["name"] == "Arquitectura de software"
    assert result["projects"][0]["name"] == "Analizador de CV"
    assert result["metadata"]["unclassified_text"] == [
        "Alex Rivera",
        "Backend Developer",
        "alex.rivera@example.test",
        "+34 612 345 678",
        "linkedin.com/in/alex-rivera",
        "github.com/alex-rivera",
        "alexrivera.dev",
    ]
    assert result["metadata"]["page_count"] == 2
    assert result["metadata"]["file_size_bytes"] > 0
    assert result["metadata"]["processed_successfully"] is True


def test_real_english_pdf_recognizes_english_headings(
    tmp_path: Path,
) -> None:
    file_path = create_text_pdf(
        tmp_path / "english-cv.pdf",
        ENGLISH_CV_PAGES,
    )

    result = process_cv_file(file_path)

    _assert_valid_json_result(result)
    assert result["personal_data"]["full_name"] == "Sam Taylor"
    assert result["personal_data"]["summary"] == (
        "Analyst focused on reliable reporting."
    )
    assert "Built operational dashboards" in (
        result["experience"][0]["description"]
    )
    assert result["education"][0]["description"] == "BSc in Statistics"
    assert result["skills"]["technical"] == ["SQL", "Power BI"]
    assert result["languages"][0] == {
        "language": "English",
        "level": "Native",
    }


def test_headerless_pdf_preserves_every_line_as_unclassified(
    tmp_path: Path,
) -> None:
    file_path = create_text_pdf(
        tmp_path / "headerless.pdf",
        HEADERLESS_CV_PAGES,
    )

    result = process_cv_file(file_path)

    _assert_valid_json_result(result)
    assert result["personal_data"]["full_name"] == "Taylor Morgan"
    assert result["personal_data"]["professional_title"] is None
    assert result["metadata"]["unclassified_text"] == (
        HEADERLESS_CV_PAGES[0].splitlines()
    )
    assert "No se detecto experiencia profesional." in (
        result["metadata"]["warnings"]
    )
    assert "No se detecto formacion academica." in (
        result["metadata"]["warnings"]
    )


def test_duplicate_sections_accumulate_content_and_emit_warning(
    tmp_path: Path,
) -> None:
    file_path = create_text_pdf(
        tmp_path / "duplicate-sections.pdf",
        DUPLICATE_SECTION_CV_PAGES,
    )

    result = process_cv_file(file_path)

    _assert_valid_json_result(result)
    description = result["experience"][0]["description"]
    assert "First role retained" in description
    assert "Second role retained" in description
    assert "Seccion duplicada detectada: experience." in (
        result["metadata"]["warnings"]
    )


def test_corrupt_pdf_returns_the_same_valid_json_contract(
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "corrupt.pdf"
    file_path.write_text("not a real PDF", encoding="utf-8")

    result = process_cv_file(file_path)

    _assert_valid_json_result(result)
    assert result["metadata"]["processed_successfully"] is False
    assert result["metadata"]["source_file"] == "corrupt.pdf"
    assert result["metadata"]["errors"]


def test_blank_pdf_returns_the_same_valid_json_contract(
    tmp_path: Path,
) -> None:
    file_path = create_blank_pdf(tmp_path / "blank.pdf")

    result = process_cv_file(file_path)

    _assert_valid_json_result(result)
    assert result["metadata"]["processed_successfully"] is False
    assert result["metadata"]["errors"] == [PDF_EMPTY_TEXT_MESSAGE]


def test_encrypted_pdf_returns_the_same_valid_json_contract(
    tmp_path: Path,
) -> None:
    file_path = create_encrypted_pdf(tmp_path / "encrypted.pdf")

    result = process_cv_file(file_path)

    _assert_valid_json_result(result)
    assert result["metadata"]["processed_successfully"] is False
    assert result["metadata"]["errors"] == [PDF_PROTECTED_MESSAGE]
