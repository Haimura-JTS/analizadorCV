from cv_analyzer.additional_sections_extractor import extract_certifications
from cv_analyzer.additional_sections_extractor import (
    extract_certifications_with_warnings,
)
from cv_analyzer.additional_sections_extractor import extract_courses
from cv_analyzer.additional_sections_extractor import (
    extract_courses_with_warnings,
)
from cv_analyzer.additional_sections_extractor import extract_languages
from cv_analyzer.additional_sections_extractor import (
    extract_languages_with_warnings,
)
from cv_analyzer.additional_sections_extractor import extract_projects
from cv_analyzer.additional_sections_extractor import (
    extract_projects_with_warnings,
)


def test_extract_languages_splits_level_when_available() -> None:
    languages = extract_languages(["Ingles - B2", "Espanol: Nativo"])

    assert languages[0].language == "Ingles"
    assert languages[0].level == "B2"
    assert languages[1].language == "Espanol"
    assert languages[1].level == "Nativo"


def test_extract_additional_sections_preserve_line_content() -> None:
    assert extract_certifications(["AZ-900"])[0].name == "AZ-900"
    assert extract_courses(["Curso de Python"])[0].name == "Curso de Python"
    assert extract_projects(["Analizador CV"])[0].description == "Analizador CV"


def test_extract_languages_supports_lists_and_warns_unknown_levels() -> None:
    result = extract_languages_with_warnings(
        ["English, Spanish", "German - Business working proficiency"]
    )

    assert [entry.language for entry in result.entries] == [
        "English",
        "Spanish",
        "German",
    ]
    assert result.entries[2].level == "Business working proficiency"
    assert result.warnings == [
        "languages[2] contiene un nivel no normalizado."
    ]


def test_extract_languages_warns_for_missing_explicit_values() -> None:
    missing_language = extract_languages_with_warnings([": C1"])
    missing_level = extract_languages_with_warnings(["English:"])

    assert missing_language.entries[0].language is None
    assert missing_language.entries[0].level == "C1"
    assert missing_language.warnings == [
        "languages[0] no incluye un idioma."
    ]
    assert missing_level.entries[0].language == "English"
    assert missing_level.entries[0].level is None
    assert missing_level.warnings == [
        "languages[0] no incluye un nivel."
    ]


def test_extract_certifications_parses_institution_and_date() -> None:
    entries = extract_certifications(
        ["Azure Fundamentals | Microsoft | 2024"]
    )

    assert entries[0].name == "Azure Fundamentals"
    assert entries[0].institution == "Microsoft"
    assert entries[0].date == "2024"


def test_extract_certifications_preserves_ambiguous_structure() -> None:
    result = extract_certifications_with_warnings(
        ["Certification | Issuer | Credential | 2024"]
    )

    assert result.entries[0].name == (
        "Certification | Issuer | Credential | 2024"
    )
    assert result.warnings == [
        "certifications[0] tiene una estructura ambigua."
    ]


def test_extract_courses_parses_ranges_and_current_status() -> None:
    dated_course = extract_courses(
        ["Python avanzado | Academia X | Jan 2023 - Mar 2023"]
    )[0]
    current_course = extract_courses(
        ["Cloud | Academia Y | 2024 - Present"]
    )[0]

    assert dated_course.name == "Python avanzado"
    assert dated_course.institution == "Academia X"
    assert dated_course.start_date == "2023-01"
    assert dated_course.end_date == "2023-03"
    assert current_course.start_date == "2024"
    assert current_course.end_date is None
    assert current_course.status == "in_progress"


def test_extract_courses_warns_for_ambiguous_structure() -> None:
    result = extract_courses_with_warnings(
        ["Curso | Centro | Modalidad | 2024"]
    )

    assert result.entries[0].name == "Curso | Centro | Modalidad | 2024"
    assert result.warnings == [
        "courses[0] tiene una estructura ambigua."
    ]


def test_extract_projects_groups_labeled_blocks_in_order() -> None:
    result = extract_projects_with_warnings(
        [
            "Proyecto: Analizador CV",
            "Descripción: Extrae información de currículums.",
            "Tecnologías: Python, PyMuPDF",
            "URL: https://example.test/cv",
            "Project: Dashboard",
            "Built operational reports.",
            "Technologies: SQL; Power BI",
        ]
    )

    assert len(result.entries) == 2
    assert result.entries[0].name == "Analizador CV"
    assert result.entries[0].description == (
        "Extrae información de currículums."
    )
    assert result.entries[0].technologies == ["Python", "PyMuPDF"]
    assert result.entries[0].url == "https://example.test/cv"
    assert result.entries[1].name == "Dashboard"
    assert result.entries[1].description == "Built operational reports."
    assert result.entries[1].technologies == ["SQL", "Power BI"]
    assert result.warnings == []


def test_extract_projects_preserves_duplicate_url_with_warning() -> None:
    result = extract_projects_with_warnings(
        [
            "Project: Demo",
            "URL: https://first.example.test",
            "URL: https://second.example.test",
        ]
    )

    assert result.entries[0].url == "https://first.example.test"
    assert result.entries[0].description == (
        "URL: https://second.example.test"
    )
    assert result.warnings == ["projects[0] contiene mas de una URL."]


def test_extract_projects_warns_when_labeled_block_has_no_name() -> None:
    result = extract_projects_with_warnings(
        ["Description: Proyecto sin titulo"]
    )

    assert result.entries[0].name is None
    assert result.entries[0].description == "Proyecto sin titulo"
    assert result.warnings == [
        "projects[0] no incluye un nombre explicito."
    ]


def test_extract_additional_sections_return_empty_lists() -> None:
    assert extract_languages([]) == []
    assert extract_certifications([]) == []
    assert extract_courses([]) == []
    assert extract_projects([]) == []
