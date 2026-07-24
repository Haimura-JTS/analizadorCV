from cv_analyzer.education_extractor import extract_education


def test_extract_education_preserves_description() -> None:
    entries = extract_education(["Grado en Informatica", "Universidad X"])

    assert len(entries) == 1
    assert entries[0].description == "Grado en Informatica\nUniversidad X"
    assert entries[0].degree is None


def test_extract_education_returns_empty_list_without_content() -> None:
    assert extract_education([]) == []

