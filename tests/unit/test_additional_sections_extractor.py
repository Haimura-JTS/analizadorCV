from cv_analyzer.additional_sections_extractor import extract_certifications
from cv_analyzer.additional_sections_extractor import extract_courses
from cv_analyzer.additional_sections_extractor import extract_languages
from cv_analyzer.additional_sections_extractor import extract_projects


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

