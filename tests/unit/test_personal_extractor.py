import pytest

from cv_analyzer.personal_extractor import extract_initial_personal_info


def test_extract_initial_personal_info_detects_name_and_title() -> None:
    result = extract_initial_personal_info(["Ana Garcia Lopez", "Python Developer"])

    assert result.full_name == "Ana Garcia Lopez"
    assert result.professional_title == "Python Developer"


def test_extract_initial_personal_info_avoids_contact_line_as_name() -> None:
    result = extract_initial_personal_info(["ana@example.com", "Python Developer"])

    assert result.full_name is None
    assert result.professional_title is None


def test_extract_initial_personal_info_skips_document_heading() -> None:
    result = extract_initial_personal_info(
        ["CURRICULUM VITAE", "Ana Garcia", "Python Developer"]
    )

    assert result.full_name == "Ana Garcia"
    assert result.professional_title == "Python Developer"


def test_extract_initial_personal_info_skips_contact_before_title() -> None:
    result = extract_initial_personal_info(
        ["Ana Garcia", "ana@example.com", "Python Developer"]
    )

    assert result.full_name == "Ana Garcia"
    assert result.professional_title == "Python Developer"


def test_extract_initial_personal_info_does_not_use_summary_as_title() -> None:
    result = extract_initial_personal_info(
        [
            "Taylor Morgan",
            "taylor.morgan@example.test",
            "Independent consultant working with Python.",
        ]
    )

    assert result.full_name == "Taylor Morgan"
    assert result.professional_title is None


def test_extract_initial_personal_info_rejects_role_as_name() -> None:
    result = extract_initial_personal_info(
        ["Backend Developer", "Sin nombre verificable"]
    )

    assert result.full_name is None
    assert result.professional_title is None


def test_extract_initial_personal_info_accepts_name_particles() -> None:
    result = extract_initial_personal_info(["Maria de la Cruz", "Data Analyst"])

    assert result.full_name == "Maria de la Cruz"
    assert result.professional_title == "Data Analyst"


def test_extract_initial_personal_info_allows_isolated_number_in_title() -> None:
    result = extract_initial_personal_info(["Ana Garcia", "Artista 3D"])

    assert result.full_name == "Ana Garcia"
    assert result.professional_title == "Artista 3D"


def test_extract_initial_personal_info_stops_title_search_at_section() -> None:
    result = extract_initial_personal_info(
        [
            "Ana Garcia",
            "ana@example.com",
            "EXPERIENCIA",
            "Empresa Demo",
        ]
    )

    assert result.full_name == "Ana Garcia"
    assert result.professional_title is None


@pytest.mark.parametrize(
    "second_line",
    [
        "ana@example.com",
        "+34 000 000 000",
        "https://example.com/ana",
        "linkedin.com/in/ana",
        "Madrid | ana@example.com",
        "EXPERIENCIA",
    ],
)
def test_extract_initial_personal_info_does_not_use_metadata_as_title(
    second_line: str,
) -> None:
    result = extract_initial_personal_info(["Ana Garcia", second_line])

    assert result.full_name == "Ana Garcia"
    assert result.professional_title is None
