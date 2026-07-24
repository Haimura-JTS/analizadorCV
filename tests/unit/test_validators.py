from cv_analyzer.contact_extractor import ContactInfo
from cv_analyzer.education_extractor import EducationEntry
from cv_analyzer.experience_extractor import ExperienceEntry
from cv_analyzer.json_builder import build_structured_cv_result
from cv_analyzer.validators import validate_and_annotate_cv_result


def test_validate_and_annotate_cv_result_adds_missing_section_warnings() -> None:
    result = build_structured_cv_result(
        full_name=None,
        professional_title=None,
        contact=ContactInfo(),
        education=[],
        experience=[],
        skills={
            "technical": [],
            "tools": [],
            "programming_languages": [],
            "soft_skills": [],
        },
        languages=[],
        certifications=[],
        courses=[],
        projects=[],
        unclassified_text=[],
    )

    report = validate_and_annotate_cv_result(result)

    assert report.errors == []
    assert "No se detectaron datos de contacto." in report.warnings
    assert "No se detecto experiencia profesional." in report.warnings
    assert report.data["metadata"]["processed_successfully"] is True


def test_validate_and_annotate_cv_result_warns_about_inverted_dates() -> None:
    result = build_structured_cv_result(
        full_name=None,
        professional_title=None,
        contact=ContactInfo(email="ana@example.com"),
        education=[EducationEntry(start_date="2024", end_date="2023")],
        experience=[ExperienceEntry(start_date="2022", end_date="2021")],
        skills={
            "technical": [],
            "tools": [],
            "programming_languages": [],
            "soft_skills": [],
        },
        languages=[],
        certifications=[],
        courses=[],
        projects=[],
        unclassified_text=[],
    )

    report = validate_and_annotate_cv_result(result)

    assert "education[0] tiene fechas invertidas." in report.warnings
    assert "experience[0] tiene fechas invertidas." in report.warnings


def test_validate_and_annotate_cv_result_normalizes_date_ranges() -> None:
    result = build_structured_cv_result(
        full_name=None,
        professional_title=None,
        contact=ContactInfo(email="ana@example.com"),
        education=[],
        experience=[
            ExperienceEntry(start_date="Jan 2023 - Present", description="Dev")
        ],
        skills={
            "technical": [],
            "tools": [],
            "programming_languages": [],
            "soft_skills": [],
        },
        languages=[],
        certifications=[],
        courses=[],
        projects=[],
        unclassified_text=[],
    )

    report = validate_and_annotate_cv_result(result)

    assert report.data["experience"][0]["start_date"] == "2023-01"
    assert report.data["experience"][0]["end_date"] is None
    assert report.data["experience"][0]["current"] is True


def test_validate_and_annotate_cv_result_preserves_existing_errors() -> None:
    result = build_structured_cv_result(
        full_name=None,
        professional_title=None,
        contact=ContactInfo(),
        education=[],
        experience=[],
        skills={
            "technical": [],
            "tools": [],
            "programming_languages": [],
            "soft_skills": [],
        },
        languages=[],
        certifications=[],
        courses=[],
        projects=[],
        unclassified_text=[],
    )
    result["metadata"]["errors"] = ["Fallo previo controlado."]

    report = validate_and_annotate_cv_result(result)

    assert report.errors == ["Fallo previo controlado."]
    assert report.data["metadata"]["processed_successfully"] is False
