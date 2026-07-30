import json

from cv_analyzer.contact_extractor import ContactInfo
from cv_analyzer.education_extractor import EducationEntry
from cv_analyzer.experience_extractor import ExperienceEntry
from cv_analyzer.json_builder import build_basic_cv_result
from cv_analyzer.json_builder import build_failed_cv_result
from cv_analyzer.json_builder import build_structured_cv_result


def test_build_basic_cv_result_is_serializable_shape() -> None:
    result = build_basic_cv_result(
        full_name="Ana Garcia",
        professional_title="Python Developer",
        contact=ContactInfo(email="ana@example.com"),
        unclassified_text=["Ana Garcia", "Python Developer"],
    )

    assert result["personal_data"]["full_name"] == "Ana Garcia"
    assert result["contact"]["email"] == "ana@example.com"
    assert result["education"] == []
    assert result["metadata"]["processed_successfully"] is True
    json.dumps(result)


def test_build_basic_cv_result_uses_null_for_missing_contact_data() -> None:
    result = build_basic_cv_result(
        full_name=None,
        professional_title=None,
        contact=ContactInfo(),
        unclassified_text=[],
    )

    assert result["personal_data"]["full_name"] is None
    assert result["personal_data"]["professional_title"] is None
    assert all(value is None for value in result["contact"].values())
    json.dumps(result)


def test_build_structured_cv_result_includes_extracted_sections() -> None:
    result = build_structured_cv_result(
        full_name="Ana Garcia",
        professional_title="Python Developer",
        contact=ContactInfo(email="ana@example.com"),
        education=[EducationEntry(description="Grado")],
        experience=[ExperienceEntry(description="Empresa")],
        skills={
            "technical": ["Python"],
            "tools": [],
            "programming_languages": [],
            "soft_skills": [],
        },
        languages=[],
        certifications=[],
        courses=[],
        projects=[],
        unclassified_text=["Ana Garcia"],
        warnings=["Seccion duplicada detectada: experience."],
    )

    assert result["education"][0]["description"] == "Grado"
    assert result["experience"][0]["description"] == "Empresa"
    assert result["skills"]["technical"] == ["Python"]
    assert result["metadata"]["warnings"] == [
        "Seccion duplicada detectada: experience."
    ]


def test_build_failed_cv_result_keeps_complete_contract() -> None:
    result = build_failed_cv_result(
        source_file="cv.pdf",
        errors=["No se pudo leer el PDF."],
        processed_at="2026-07-24T10:00:00+00:00",
        file_size_bytes=512,
    )

    assert result["personal_data"]["full_name"] is None
    assert result["experience"] == []
    assert result["metadata"]["source_file"] == "cv.pdf"
    assert result["metadata"]["file_size_bytes"] == 512
    assert result["metadata"]["processed_successfully"] is False
    assert result["metadata"]["errors"] == ["No se pudo leer el PDF."]


def test_builders_copy_mutable_input_collections() -> None:
    unclassified_text = ["Ana Garcia"]
    skills = {
        "technical": ["FastAPI"],
        "tools": [],
        "programming_languages": ["Python"],
        "soft_skills": [],
    }
    warnings = ["Aviso inicial."]

    basic_result = build_basic_cv_result(
        full_name=None,
        professional_title=None,
        contact=ContactInfo(),
        unclassified_text=unclassified_text,
    )
    structured_result = build_structured_cv_result(
        full_name=None,
        professional_title=None,
        contact=ContactInfo(),
        education=[],
        experience=[],
        skills=skills,
        languages=[],
        certifications=[],
        courses=[],
        projects=[],
        unclassified_text=unclassified_text,
        warnings=warnings,
    )

    unclassified_text.append("Linea posterior")
    skills["technical"].append("Django")
    warnings.append("Aviso posterior.")

    assert basic_result["metadata"]["unclassified_text"] == ["Ana Garcia"]
    assert structured_result["metadata"]["unclassified_text"] == [
        "Ana Garcia"
    ]
    assert structured_result["skills"]["technical"] == ["FastAPI"]
    assert structured_result["metadata"]["warnings"] == ["Aviso inicial."]
