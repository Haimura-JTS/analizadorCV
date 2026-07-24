from cv_analyzer.personal_extractor import extract_initial_personal_info


def test_extract_initial_personal_info_detects_name_and_title() -> None:
    result = extract_initial_personal_info(["Ana Garcia Lopez", "Python Developer"])

    assert result.full_name == "Ana Garcia Lopez"
    assert result.professional_title == "Python Developer"


def test_extract_initial_personal_info_avoids_contact_line_as_name() -> None:
    result = extract_initial_personal_info(["ana@example.com", "Python Developer"])

    assert result.full_name is None
    assert result.professional_title is None

