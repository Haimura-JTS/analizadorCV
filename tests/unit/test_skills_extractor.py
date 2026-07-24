from cv_analyzer.skills_extractor import extract_skills


def test_extract_skills_splits_and_deduplicates_values() -> None:
    result = extract_skills(["Python, SQL", "python; Docker"])

    assert result["technical"] == ["Python", "SQL", "Docker"]
    assert result["tools"] == []

