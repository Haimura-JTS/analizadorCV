from cv_analyzer.experience_extractor import extract_experience
from cv_analyzer.experience_extractor import (
    extract_experience_with_warnings,
)


def test_extract_experience_preserves_description_and_bullets() -> None:
    entries = extract_experience(
        [
            "Backend Developer - Empresa A",
            "- Desarrollo de APIs",
            "- Automatizacion de pruebas",
        ]
    )

    assert len(entries) == 1
    assert entries[0].company == "Empresa A"
    assert entries[0].position == "Backend Developer"
    assert entries[0].description == (
        "Backend Developer - Empresa A\n"
        "- Desarrollo de APIs\n"
        "- Automatizacion de pruebas"
    )
    assert entries[0].responsibilities == [
        "Desarrollo de APIs",
        "Automatizacion de pruebas",
    ]


def test_extract_experience_returns_empty_list_without_content() -> None:
    assert extract_experience(["", "  "]) == []


def test_extract_experience_separates_entries_dates_and_bullet_types() -> None:
    result = extract_experience_with_warnings(
        [
            "Ingeniero de Software",
            "Empresa Uno",
            "ene. 2020 - dic. 2022",
            "- Desarrollo de APIs",
            "Senior Engineer",
            "Empresa Dos",
            "2023 - Present",
            "- Improved response time by 30%",
        ]
    )

    assert len(result.entries) == 2
    assert result.entries[0].company == "Empresa Uno"
    assert result.entries[0].position == "Ingeniero de Software"
    assert result.entries[0].start_date == "2020-01"
    assert result.entries[0].end_date == "2022-12"
    assert result.entries[0].responsibilities == ["Desarrollo de APIs"]
    assert result.entries[1].company == "Empresa Dos"
    assert result.entries[1].position == "Senior Engineer"
    assert result.entries[1].start_date == "2023"
    assert result.entries[1].end_date is None
    assert result.entries[1].current is True
    assert result.entries[1].achievements == [
        "Improved response time by 30%"
    ]
    assert result.warnings == []


def test_extract_experience_warns_without_guessing_ambiguous_header() -> None:
    result = extract_experience_with_warnings(
        ["Empresa Uno - Empresa Dos", "- Tareas generales"]
    )

    assert result.entries[0].company is None
    assert result.entries[0].position is None
    assert result.warnings == [
        "experience[0] no permite diferenciar empresa y puesto."
    ]
