from cv_analyzer.experience_extractor import extract_experience


def test_extract_experience_preserves_description_and_bullets() -> None:
    entries = extract_experience(
        [
            "Backend Developer - Empresa A",
            "- Desarrollo de APIs",
            "- Automatizacion de pruebas",
        ]
    )

    assert len(entries) == 1
    assert entries[0].description == (
        "Backend Developer - Empresa A\n"
        "- Desarrollo de APIs\n"
        "- Automatizacion de pruebas"
    )
    assert entries[0].responsibilities == [
        "Desarrollo de APIs",
        "Automatizacion de pruebas",
    ]


def test_extract_experience_returns_empty_list_without_content() -> None:
    assert extract_experience(["", "  "]) == []

