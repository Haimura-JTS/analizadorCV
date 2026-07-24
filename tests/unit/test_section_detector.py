from cv_analyzer.section_detector import detect_sections
from cv_analyzer.section_detector import detect_sections_with_warnings
from cv_analyzer.section_detector import find_section_name, normalize_heading


def test_normalize_heading_removes_case_colon_spaces_and_accents() -> None:
    heading = "  FORMACI\u00d3N ACAD\u00c9MICA: "

    assert normalize_heading(heading) == "formacion academica"


def test_find_section_name_detects_known_aliases() -> None:
    assert find_section_name("Experiencia profesional") == "experience"
    assert find_section_name("Technical Skills") == "skills"
    assert find_section_name("Idiomas:") == "languages"


def test_find_section_name_does_not_match_partial_sentences() -> None:
    assert find_section_name("Tengo experiencia con Python") is None


def test_detect_sections_keeps_unclassified_text_before_first_heading() -> None:
    lines = [
        "Ana Garcia",
        "Python Developer",
        "Experiencia",
        "Empresa A",
    ]

    sections = detect_sections(lines)

    assert sections["unclassified"] == ["Ana Garcia", "Python Developer"]
    assert sections["experience"] == ["Empresa A"]


def test_detect_sections_groups_main_sections() -> None:
    lines = [
        "Perfil",
        "Desarrolladora backend",
        "Formacion academica",
        "Grado en Informatica",
        "Proyectos",
        "Analizador de CV",
    ]

    sections = detect_sections(lines)

    assert sections["profile"] == ["Desarrolladora backend"]
    assert sections["education"] == ["Grado en Informatica"]
    assert sections["projects"] == ["Analizador de CV"]


def test_detect_sections_accumulates_duplicate_sections_and_warns() -> None:
    lines = [
        "Experiencia",
        "Empresa A",
        "Experiencia profesional",
        "Empresa B",
    ]

    result = detect_sections_with_warnings(lines)

    assert result.sections["experience"] == ["Empresa A", "Empresa B"]
    assert result.warnings == ["Seccion duplicada detectada: experience."]
