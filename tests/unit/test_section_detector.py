import pytest

from cv_analyzer.section_detector import SECTION_ALIASES
from cv_analyzer.section_detector import detect_sections
from cv_analyzer.section_detector import detect_sections_with_warnings
from cv_analyzer.section_detector import find_section_name, normalize_heading


def test_section_aliases_are_unique_across_sections() -> None:
    alias_owners: dict[str, str] = {}

    for section_name, aliases in SECTION_ALIASES.items():
        for alias in aliases:
            assert alias not in alias_owners, (
                f"Alias duplicado: {alias} pertenece a "
                f"{alias_owners.get(alias)} y {section_name}."
            )
            alias_owners[alias] = section_name


def test_normalize_heading_removes_case_colon_spaces_and_accents() -> None:
    heading = "  FORMACI\u00d3N ACAD\u00c9MICA: "

    assert normalize_heading(heading) == "formacion academica"


def test_normalize_heading_removes_numbering_and_decoration() -> None:
    heading = "  • 1. FORMACI\u00d3N ACAD\u00c9MICA: • "

    assert normalize_heading(heading) == "formacion academica"


@pytest.mark.parametrize(
    ("heading", "expected_section"),
    [
        ("Acerca de mi", "profile"),
        ("Trayectoria profesional", "experience"),
        ("Qualifications", "education"),
        ("Skills & Tools", "skills"),
        ("Language Skills", "languages"),
        ("Licenses & Certifications", "certifications"),
        ("Professional Development", "courses"),
        ("Project Experience", "projects"),
    ],
)
def test_find_section_name_detects_known_aliases(
    heading: str,
    expected_section: str,
) -> None:
    assert find_section_name(heading) == expected_section


@pytest.mark.parametrize(
    ("heading", "expected_section"),
    [
        ("Experiencia / Work Experience", "experience"),
        ("Habilidades (Technical Skills)", "skills"),
        ("Idiomas | Languages", "languages"),
    ],
)
def test_find_section_name_detects_equivalent_bilingual_headings(
    heading: str,
    expected_section: str,
) -> None:
    assert find_section_name(heading) == expected_section


def test_find_section_name_does_not_match_partial_sentences() -> None:
    assert find_section_name("Tengo experiencia con Python") is None
    assert find_section_name("Skills developed during projects") is None


@pytest.mark.parametrize(
    ("line", "expected_section", "expected_content"),
    [
        ("Idiomas y nivel: Ingles B2", "languages", "Ingles B2"),
        (
            "FORMACION Y ESTUDIOS | Grado en Datos | Universidad X",
            "education",
            "Grado en Datos | Universidad X",
        ),
        (
            "Licencias y certificaciones - AWS Cloud Practitioner",
            "certifications",
            "AWS Cloud Practitioner",
        ),
        (
            "Formacion adicional: Curso de Python",
            "courses",
            "Curso de Python",
        ),
    ],
)
def test_detect_sections_supports_inline_headings(
    line: str,
    expected_section: str,
    expected_content: str,
) -> None:
    result = detect_sections_with_warnings([line])

    assert find_section_name(line) == expected_section
    assert result.sections[expected_section] == [expected_content]
    assert result.section_order == [expected_section]


def test_detect_sections_supports_bilingual_inline_heading() -> None:
    result = detect_sections(
        ["Idiomas | Languages: English - Professional"]
    )

    assert result["languages"] == ["English - Professional"]


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
    assert result.section_order == ["experience", "experience"]


def test_detect_sections_preserves_order_of_detected_sections() -> None:
    lines = [
        "Perfil",
        "Profesional orientada a servicios",
        "Experiencia",
        "Empresa A",
        "Habilidades",
        "Python",
    ]

    result = detect_sections_with_warnings(lines)

    assert result.section_order == ["profile", "experience", "skills"]


def test_detect_sections_keeps_ambiguous_heading_unclassified() -> None:
    lines = [
        "Perfil",
        "Resumen profesional",
        "Experiencia / Formacion",
        "Contenido combinado",
        "Skills",
        "Python",
    ]

    result = detect_sections_with_warnings(lines)

    assert result.sections["profile"] == ["Resumen profesional"]
    assert result.sections["unclassified"] == [
        "Experiencia / Formacion",
        "Contenido combinado",
    ]
    assert result.sections["skills"] == ["Python"]
    assert result.warnings == [
        "Encabezado ambiguo conservado sin clasificar: "
        "experiencia / formacion."
    ]
    assert result.section_order == ["profile", "skills"]


def test_detect_sections_preserves_unknown_heading_in_active_section() -> None:
    lines = [
        "Experiencia",
        "DIVISION INTERNACIONAL",
        "Desarrollo de servicios",
    ]

    result = detect_sections_with_warnings(lines)

    assert result.sections["experience"] == [
        "DIVISION INTERNACIONAL",
        "Desarrollo de servicios",
    ]
    assert result.warnings == []
