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

