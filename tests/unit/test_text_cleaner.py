from cv_analyzer.text_cleaner import clean_text, split_clean_lines


def test_clean_text_reduces_spaces_and_removes_empty_lines() -> None:
    text = "  Ana   Garcia  \n\n Python   Developer \n"

    assert clean_text(text) == "Ana Garcia\nPython Developer"


def test_split_clean_lines_returns_non_empty_lines() -> None:
    text = "Uno\n\n  Dos  \n"

    assert split_clean_lines(text) == ["Uno", "Dos"]


def test_clean_text_removes_invisible_and_unsupported_characters() -> None:
    text = "Ana\u200b Garcia\u00ad\nPython\u0000 Developer"

    assert clean_text(text) == "Ana Garcia\nPython Developer"


def test_clean_text_normalizes_non_breaking_spaces_and_tabs() -> None:
    text = "Ana\u00a0\u00a0Garcia\nPython\tDeveloper"

    assert clean_text(text) == "Ana Garcia\nPython Developer"


def test_clean_text_returns_empty_string_for_empty_content() -> None:
    assert clean_text("\u200b\n\t\n") == ""
