from cv_analyzer.text_cleaner import clean_text, split_clean_lines


def test_clean_text_reduces_spaces_and_removes_empty_lines() -> None:
    text = "  Ana   Garcia  \n\n Python   Developer \n"

    assert clean_text(text) == "Ana Garcia\nPython Developer"


def test_split_clean_lines_returns_non_empty_lines() -> None:
    text = "Uno\n\n  Dos  \n"

    assert split_clean_lines(text) == ["Uno", "Dos"]

