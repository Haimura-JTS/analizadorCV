from cv_analyzer.education_extractor import extract_education
from cv_analyzer.education_extractor import extract_education_with_warnings


def test_extract_education_preserves_description() -> None:
    entries = extract_education(["Grado en Informatica", "Universidad X"])

    assert len(entries) == 1
    assert entries[0].description == "Grado en Informatica\nUniversidad X"
    assert entries[0].degree == "Grado en Informatica"
    assert entries[0].institution == "Universidad X"


def test_extract_education_returns_empty_list_without_content() -> None:
    assert extract_education([]) == []


def test_extract_education_separates_entries_and_normalizes_dates() -> None:
    result = extract_education_with_warnings(
        [
            "Master en Inteligencia Artificial",
            "Universidad X",
            "2021 - 2022",
            "Grado en Informatica",
            "Instituto Y",
            "2017 - 2021",
        ]
    )

    assert len(result.entries) == 2
    assert result.entries[0].degree == "Master en Inteligencia Artificial"
    assert result.entries[0].institution == "Universidad X"
    assert result.entries[0].start_date == "2021"
    assert result.entries[0].end_date == "2022"
    assert result.entries[1].degree == "Grado en Informatica"
    assert result.entries[1].institution == "Instituto Y"
    assert result.entries[1].start_date == "2017"
    assert result.entries[1].end_date == "2021"
    assert result.warnings == []


def test_extract_education_marks_current_study_and_ambiguity() -> None:
    current_result = extract_education_with_warnings(
        ["Máster en Datos | Universidad X | 2024 - Actualidad"]
    )
    ambiguous_result = extract_education_with_warnings(
        ["Programa avanzado", "Centro X", "2024"]
    )

    assert current_result.entries[0].status == "in_progress"
    assert current_result.entries[0].start_date == "2024"
    assert current_result.entries[0].end_date is None
    assert current_result.warnings == []
    assert ambiguous_result.entries[0].institution is None
    assert ambiguous_result.entries[0].degree is None
    assert ambiguous_result.warnings == [
        "education[0] no permite diferenciar institucion y titulacion."
    ]
