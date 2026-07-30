import json
from pathlib import Path

import fitz

from cv_analyzer.constants import PDF_EMPTY_TEXT_MESSAGE, PDF_PROTECTED_MESSAGE
from cv_analyzer.constants import PDF_SCANNED_MESSAGE
from cv_analyzer.constants import PDF_SCANNED_PAGES_WARNING_TEMPLATE
from cv_analyzer.models import CVResultModel
from cv_analyzer.pipeline import process_cv_file, process_cv_file_with_details
from tests.fixtures.cv_samples import (
    DUPLICATE_SECTION_CV_PAGES,
    ENGLISH_CV_PAGES,
    HEADERLESS_CV_PAGES,
    MULTI_EXPERIENCE_CV_PAGES,
    SPARSE_CV_PAGES,
    SPANISH_CV_PAGES,
)
from tests.fixtures.pdf_factory import (
    create_blank_pdf,
    create_encrypted_pdf,
    create_image_only_pdf,
    create_partially_scanned_pdf,
    create_text_pdf,
    create_two_column_text_pdf,
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
        "phone": "+34 000 000 000",
        "linkedin": "https://linkedin.com/in/cv-test-alex-rivera",
        "github": "https://github.com/cv-test-alex-rivera",
        "portfolio": "https://alexrivera.dev",
    }
    assert result["experience"][0]["responsibilities"] == [
        "Desarrollo de APIs en Python"
    ]
    assert result["experience"][0]["company"] == "Northwind Labs"
    assert result["experience"][0]["position"] == "Backend Developer"
    assert "Northwind Labs - Backend Developer" in (
        result["experience"][0]["description"]
    )
    assert result["education"][0]["description"] == (
        "Grado en Ingenieria Informatica"
    )
    assert result["education"][0]["degree"] == (
        "Grado en Ingenieria Informatica"
    )
    assert result["skills"]["technical"] == ["FastAPI"]
    assert result["skills"]["tools"] == ["PostgreSQL"]
    assert result["skills"]["programming_languages"] == ["Python"]
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
        "+34 000 000 000",
        "linkedin.com/in/cv-test-alex-rivera",
        "github.com/cv-test-alex-rivera",
        "alexrivera.dev",
    ]
    assert result["metadata"]["page_count"] == 2
    assert result["metadata"]["file_size_bytes"] > 0
    assert result["metadata"]["processed_successfully"] is True
    assert (
        "education[0] no permite diferenciar institucion y titulacion."
        in result["metadata"]["warnings"]
    )


def test_real_pdf_detects_inline_sections_and_hidden_linkedin(
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "modern-inline-cv.pdf"
    document = fitz.open()
    page = document.new_page()
    cv_lines = [
        "Ana Garcia",
        "Backend Developer",
        "FORMACION Y ESTUDIOS: Tecnico Superior en Desarrollo Web | "
        "IES Clara Campoamor | 2020 - 2022",
        "COMPETENCIAS PROFESIONALES: Python / FastAPI / Docker / Jira / "
        "Comunicacion efectiva",
        "IDIOMAS Y NIVEL: Ingles (B2); Espanol - Nativo",
        "LICENCIAS Y CERTIFICACIONES: AWS Cloud Practitioner | "
        "Amazon Web Services | 2024",
        "FORMACION ADICIONAL: Python avanzado | Academia X | 2023",
    ]
    for line_number, line in enumerate(cv_lines):
        page.insert_text((52, 72 + line_number * 28), line, fontsize=8)
    page.insert_link(
        {
            "kind": fitz.LINK_URI,
            "from": fitz.Rect(45, 42, 90, 62),
            "uri": "https://www.linkedin.com/in/ana-garcia",
        }
    )
    document.save(file_path)
    document.close()

    result = process_cv_file(file_path)

    _assert_valid_json_result(result)
    assert result["contact"]["linkedin"] == (
        "https://www.linkedin.com/in/ana-garcia"
    )
    assert result["education"][0]["degree"] == (
        "Tecnico Superior en Desarrollo Web"
    )
    assert result["education"][0]["institution"] == "IES Clara Campoamor"
    assert result["skills"]["programming_languages"] == ["Python"]
    assert result["skills"]["technical"] == ["FastAPI"]
    assert result["skills"]["tools"] == ["Docker", "Jira"]
    assert result["skills"]["soft_skills"] == ["Comunicacion efectiva"]
    assert result["languages"] == [
        {"language": "Ingles", "level": "B2"},
        {"language": "Espanol", "level": "Nativo"},
    ]
    assert result["certifications"][0]["name"] == "AWS Cloud Practitioner"
    assert result["certifications"][0]["institution"] == (
        "Amazon Web Services"
    )
    assert result["courses"][0]["name"] == "Python avanzado"
    assert result["courses"][0]["institution"] == "Academia X"
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
    assert result["experience"][0]["company"] == "Contoso"
    assert result["experience"][0]["position"] == "Data Analyst"
    assert result["education"][0]["description"] == "BSc in Statistics"
    assert result["education"][0]["degree"] == "BSc in Statistics"
    assert result["skills"]["programming_languages"] == ["SQL"]
    assert result["skills"]["tools"] == ["Power BI"]
    assert result["languages"][0] == {
        "language": "English",
        "level": "Native",
    }


def test_decorated_and_bilingual_headings_run_through_pipeline(
    tmp_path: Path,
) -> None:
    file_path = create_text_pdf(
        tmp_path / "decorated-headings.pdf",
        [
            """\
Alex Demo
alex.demo@example.test
• 1. PERFIL •
Desarrollador de servicios fiables.
II) EXPERIENCE / EXPERIENCIA
Demo Corp
3 - SKILLS & TOOLS
Python, SQL
"""
        ],
    )

    result = process_cv_file(file_path)

    _assert_valid_json_result(result)
    assert result["personal_data"]["full_name"] == "Alex Demo"
    assert result["personal_data"]["summary"] == (
        "Desarrollador de servicios fiables."
    )
    assert result["experience"][0]["description"] == "Demo Corp"
    assert result["skills"]["programming_languages"] == ["Python", "SQL"]
    assert result["metadata"]["processed_successfully"] is True


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


def test_two_column_pdf_preserves_text_and_structures_known_sections(
    tmp_path: Path,
) -> None:
    left_text = """\
Casey Demo
Data Engineer
casey.demo@example.test
EXPERIENCE
Northwind Labs - Data Engineer
2020 - 2022
- Built data pipelines
"""
    right_text = """\
EDUCATION
BSc in Computing | Example University
2016 - 2020
TECHNICAL SKILLS
Python, SQL
"""
    file_path = create_two_column_text_pdf(
        tmp_path / "two-columns.pdf",
        left_text,
        right_text,
    )

    output = process_cv_file_with_details(file_path)
    result = output.data

    _assert_valid_json_result(result)
    assert output.extracted_text is not None
    expected_lines = left_text.splitlines() + right_text.splitlines()
    assert all(line in output.extracted_text for line in expected_lines)
    assert result["experience"][0]["company"] == "Northwind Labs"
    assert result["experience"][0]["description"] == (
        "Northwind Labs - Data Engineer\n"
        "2020 - 2022\n"
        "- Built data pipelines"
    )
    assert result["education"][0]["institution"] == "Example University"
    assert result["education"][0]["description"] == (
        "BSc in Computing | Example University\n2016 - 2020"
    )
    assert result["skills"]["programming_languages"] == ["Python", "SQL"]
    assert result["metadata"]["processed_successfully"] is True


def test_real_pdf_preserves_multiple_experiences_and_missing_education(
    tmp_path: Path,
) -> None:
    file_path = create_text_pdf(
        tmp_path / "multiple-experiences.pdf",
        MULTI_EXPERIENCE_CV_PAGES,
    )

    result = process_cv_file(file_path)

    _assert_valid_json_result(result)
    assert [
        (entry["company"], entry["position"])
        for entry in result["experience"]
    ] == [
        ("Northwind Labs", "Backend Developer"),
        ("Contoso", "Senior Engineer"),
    ]
    assert result["experience"][1]["current"] is True
    assert result["education"] == []
    assert "No se detecto formacion academica." in (
        result["metadata"]["warnings"]
    )


def test_sparse_pdf_keeps_missing_contact_and_experience_explicit(
    tmp_path: Path,
) -> None:
    file_path = create_text_pdf(
        tmp_path / "sparse.pdf",
        SPARSE_CV_PAGES,
    )

    result = process_cv_file(file_path)

    _assert_valid_json_result(result)
    assert result["contact"] == {
        "email": None,
        "phone": None,
        "linkedin": None,
        "github": None,
        "portfolio": None,
    }
    assert result["experience"] == []
    assert result["education"][0]["degree"] == "Bachelor of Design"
    assert result["skills"]["tools"] == ["Figma"]
    assert "No se detecto experiencia profesional." in (
        result["metadata"]["warnings"]
    )


def test_valid_pdf_with_non_pdf_extension_returns_contractual_error(
    tmp_path: Path,
) -> None:
    original_path = create_text_pdf(
        tmp_path / "curriculum.pdf",
        SPARSE_CV_PAGES,
    )
    fake_extension_path = original_path.replace(
        tmp_path / "curriculum.txt"
    )

    result = process_cv_file(fake_extension_path)

    _assert_valid_json_result(result)
    assert result["metadata"]["processed_successfully"] is False
    assert result["metadata"]["errors"] == [
        "El archivo debe tener extension PDF."
    ]


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


def test_image_only_pdf_returns_specific_scanned_error(
    tmp_path: Path,
) -> None:
    file_path = create_image_only_pdf(tmp_path / "scanned.pdf")

    result = process_cv_file(file_path)

    _assert_valid_json_result(result)
    assert result["metadata"]["processed_successfully"] is False
    assert result["metadata"]["errors"] == [PDF_SCANNED_MESSAGE]


def test_partially_scanned_pdf_preserves_warning(
    tmp_path: Path,
) -> None:
    file_path = create_partially_scanned_pdf(tmp_path / "partial-scan.pdf")

    output = process_cv_file_with_details(file_path)
    result = output.data

    _assert_valid_json_result(result)
    assert output.extracted_text == "Synthetic CV with text"
    assert result["metadata"]["processed_successfully"] is True
    assert PDF_SCANNED_PAGES_WARNING_TEMPLATE.format(pages="2") in (
        result["metadata"]["warnings"]
    )


def test_encrypted_pdf_returns_the_same_valid_json_contract(
    tmp_path: Path,
) -> None:
    file_path = create_encrypted_pdf(tmp_path / "encrypted.pdf")

    result = process_cv_file(file_path)

    _assert_valid_json_result(result)
    assert result["metadata"]["processed_successfully"] is False
    assert result["metadata"]["errors"] == [PDF_PROTECTED_MESSAGE]
