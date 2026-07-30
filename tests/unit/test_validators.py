from copy import deepcopy

from cv_analyzer.additional_sections_extractor import CertificationEntry
from cv_analyzer.additional_sections_extractor import CourseEntry, ProjectEntry
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


def test_validate_dates_marks_current_entries_in_all_supported_sections() -> None:
    result = build_structured_cv_result(
        full_name=None,
        professional_title=None,
        contact=ContactInfo(email="ana@example.com"),
        education=[
            EducationEntry(start_date="2020", end_date="Actualidad")
        ],
        experience=[
            ExperienceEntry(start_date="Jan 2023", end_date="PRESENT")
        ],
        skills={
            "technical": [],
            "tools": [],
            "programming_languages": [],
            "soft_skills": [],
        },
        languages=[],
        certifications=[],
        courses=[CourseEntry(start_date="2024", end_date="Current")],
        projects=[],
        unclassified_text=[],
    )

    report = validate_and_annotate_cv_result(result)

    assert report.data["experience"][0]["start_date"] == "2023-01"
    assert report.data["experience"][0]["end_date"] is None
    assert report.data["experience"][0]["current"] is True
    assert report.data["education"][0]["end_date"] is None
    assert report.data["education"][0]["status"] == "in_progress"
    assert report.data["courses"][0]["end_date"] is None
    assert report.data["courses"][0]["status"] == "in_progress"


def test_validate_dates_nulls_ambiguous_values_with_indexed_warnings() -> None:
    result = build_structured_cv_result(
        full_name=None,
        professional_title=None,
        contact=ContactInfo(email="ana@example.com"),
        education=[],
        experience=[ExperienceEntry(start_date="primavera 2024")],
        skills={
            "technical": [],
            "tools": [],
            "programming_languages": [],
            "soft_skills": [],
        },
        languages=[],
        certifications=[CertificationEntry(name="Demo", date="sin fecha")],
        courses=[],
        projects=[],
        unclassified_text=[],
    )

    report = validate_and_annotate_cv_result(result)

    assert report.data["experience"][0]["start_date"] is None
    assert report.data["certifications"][0]["date"] is None
    assert (
        "experience[0].start_date contiene una fecha ambigua: "
        "primavera 2024."
    ) in report.warnings
    assert (
        "certifications[0].date contiene una fecha ambigua: sin fecha."
    ) in report.warnings


def test_validate_dates_avoids_false_inversion_for_partial_year() -> None:
    result = build_structured_cv_result(
        full_name=None,
        professional_title=None,
        contact=ContactInfo(email="ana@example.com"),
        education=[
            EducationEntry(start_date="2024-12", end_date="2024")
        ],
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

    assert "education[0] tiene fechas invertidas." not in report.warnings


def test_validate_dates_warns_about_current_status_with_end_date() -> None:
    result = build_structured_cv_result(
        full_name=None,
        professional_title=None,
        contact=ContactInfo(email="ana@example.com"),
        education=[
            EducationEntry(
                start_date="2023",
                end_date="2024",
                status="in_progress",
            )
        ],
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

    assert (
        "education[0] indica actualidad y fecha final."
        in report.warnings
    )


def test_validate_deduplicates_only_controlled_lists() -> None:
    result = build_structured_cv_result(
        full_name=None,
        professional_title=None,
        contact=ContactInfo(email="ana@example.com"),
        education=[],
        experience=[
            ExperienceEntry(
                responsibilities=["APIs", "apis"],
                achievements=["Reduced 20%", "Reduced 20%"],
            ),
            ExperienceEntry(description="Entrada repetida"),
            ExperienceEntry(description="Entrada repetida"),
        ],
        skills={
            "technical": ["FastAPI", "fastapi"],
            "tools": [],
            "programming_languages": [],
            "soft_skills": [],
        },
        languages=[],
        certifications=[],
        courses=[],
        projects=[
            ProjectEntry(technologies=["Python", "python", "SQL"])
        ],
        unclassified_text=["Linea", "Linea"],
        warnings=["Aviso previo", "Aviso previo"],
    )
    original_result = deepcopy(result)

    report = validate_and_annotate_cv_result(result)

    assert report.data["skills"]["technical"] == ["FastAPI"]
    assert report.data["experience"][0]["responsibilities"] == ["APIs"]
    assert report.data["experience"][0]["achievements"] == ["Reduced 20%"]
    assert report.data["projects"][0]["technologies"] == ["Python", "SQL"]
    assert len(report.data["experience"]) == 3
    assert report.data["metadata"]["unclassified_text"] == ["Linea", "Linea"]
    assert "Se eliminaron duplicados de skills.technical." in report.warnings
    assert result == original_result


def test_validate_reports_strict_schema_errors_with_field_paths() -> None:
    result = build_structured_cv_result(
        full_name=None,
        professional_title=None,
        contact=ContactInfo(email="ana@example.com"),
        education=[],
        experience=[ExperienceEntry()],
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
    result["metadata"]["page_count"] = "2"
    result["experience"][0]["current"] = "yes"

    report = validate_and_annotate_cv_result(result)

    assert "metadata.page_count: se esperaba un numero entero." in (
        report.errors
    )
    assert "experience.0.current: se esperaba un valor booleano." in (
        report.errors
    )
    assert report.data["metadata"]["processed_successfully"] is False
