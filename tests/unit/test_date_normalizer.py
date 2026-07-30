from cv_analyzer.date_normalizer import is_current_date
from cv_analyzer.date_normalizer import is_date_range_inverted
from cv_analyzer.date_normalizer import normalize_date, normalize_date_range


def test_normalize_date_accepts_numeric_and_textual_formats() -> None:
    assert normalize_date("2024-01") == "2024-01"
    assert normalize_date("01/2024") == "2024-01"
    assert normalize_date("Enero 2024") == "2024-01"
    assert normalize_date("ene. 2024") == "2024-01"
    assert normalize_date("Jan 2024") == "2024-01"
    assert normalize_date("2024") == "2024"


def test_normalize_date_returns_none_for_ambiguous_values() -> None:
    assert normalize_date("primavera 2024") is None
    assert normalize_date("2024-13") is None
    assert normalize_date("") is None
    assert normalize_date(None) is None


def test_normalize_date_range_detects_current_period() -> None:
    result = normalize_date_range("2023 - Actualidad")

    assert result.start_date == "2023"
    assert result.end_date is None
    assert result.current is True
    assert result.warnings == []


def test_normalize_date_range_warns_about_ambiguous_parts() -> None:
    result = normalize_date_range("inicio - final")

    assert result.start_date is None
    assert result.end_date is None
    assert result.current is False
    assert result.warnings == [
        "Fecha inicial ambigua: inicio.",
        "Fecha final ambigua: final.",
    ]


def test_normalize_date_range_accepts_case_and_alternative_separators() -> None:
    english_result = normalize_date_range("JAN 2023 TO CURRENT")
    spanish_result = normalize_date_range("2020 hasta 2022")

    assert english_result.start_date == "2023-01"
    assert english_result.end_date is None
    assert english_result.current is True
    assert english_result.warnings == []
    assert spanish_result.start_date == "2020"
    assert spanish_result.end_date == "2022"


def test_normalize_date_range_handles_empty_and_single_values() -> None:
    empty_result = normalize_date_range(" ")
    single_result = normalize_date_range("2024")

    assert empty_result.start_date is None
    assert empty_result.warnings == ["Rango de fechas vacio."]
    assert single_result.start_date == "2024"
    assert single_result.end_date is None
    assert single_result.current is False
    assert single_result.warnings == []


def test_is_current_date_requires_a_complete_known_alias() -> None:
    assert is_current_date("PRESENTE") is True
    assert is_current_date("Actualidad") is True
    assert is_current_date("currently") is False
    assert is_current_date(None) is False


def test_is_date_range_inverted_respects_partial_precision() -> None:
    assert is_date_range_inverted("2025-01", "2024") is True
    assert is_date_range_inverted("2024-12", "2024") is False
    assert is_date_range_inverted("2024", "2024-01") is False
    assert is_date_range_inverted("fecha", "2024") is False
