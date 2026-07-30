from cv_analyzer.skills_extractor import extract_skills
from cv_analyzer.skills_extractor import extract_skills_with_warnings


def test_extract_skills_splits_and_deduplicates_values() -> None:
    result = extract_skills(["Python, SQL", "python; Docker"])

    assert result["technical"] == []
    assert result["programming_languages"] == ["Python", "SQL"]
    assert result["tools"] == ["Docker"]


def test_extract_skills_respects_explicit_labels_and_accents() -> None:
    result = extract_skills(
        [
            "Lenguajes de programación: Python, TypeScript",
            "Herramientas: Docker, Git",
            "Habilidades blandas: Comunicación, Trabajo en equipo",
            "Frameworks: FastAPI",
        ]
    )

    assert result == {
        "technical": ["FastAPI"],
        "tools": ["Docker", "Git"],
        "programming_languages": ["Python", "TypeScript"],
        "soft_skills": ["Comunicación", "Trabajo en equipo"],
    }


def test_extract_skills_warns_for_unknown_label_and_keeps_values() -> None:
    result = extract_skills_with_warnings(["Otros: Python, Docker"])

    assert result.skills["programming_languages"] == ["Python"]
    assert result.skills["tools"] == ["Docker"]
    assert result.warnings == [
        "skills contiene una etiqueta no reconocida; "
        "se aplico clasificacion por valor."
    ]


def test_extract_skills_returns_all_categories_when_empty() -> None:
    assert extract_skills([]) == {
        "technical": [],
        "tools": [],
        "programming_languages": [],
        "soft_skills": [],
    }


def test_extract_skills_keeps_the_first_explicit_classification() -> None:
    result = extract_skills(
        [
            "Programming languages: Docker",
            "Tools: docker",
        ]
    )

    assert result["programming_languages"] == ["Docker"]
    assert result["tools"] == []


def test_extract_skills_classifies_mixed_umbrella_label() -> None:
    result = extract_skills(
        [
            "Tecnologias y herramientas: Python / FastAPI / Docker / Jira",
            "Competencias: Comunicacion efectiva; Liderazgo; SQL Server",
        ]
    )

    assert result == {
        "technical": ["FastAPI"],
        "tools": ["Docker", "Jira", "SQL Server"],
        "programming_languages": ["Python"],
        "soft_skills": ["Comunicacion efectiva", "Liderazgo"],
    }


def test_extract_skills_recognizes_levels_without_changing_display_value() -> None:
    result = extract_skills(
        ["Python (avanzado), Docker - intermedio, Trabajo en equipo"]
    )

    assert result["programming_languages"] == ["Python (avanzado)"]
    assert result["tools"] == ["Docker - intermedio"]
    assert result["soft_skills"] == ["Trabajo en equipo"]
