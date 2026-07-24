from cv_analyzer.contact_extractor import ContactInfo
from cv_analyzer.json_builder import build_basic_cv_result


def test_build_basic_cv_result_is_serializable_shape() -> None:
    result = build_basic_cv_result(
        full_name="Ana Garcia",
        professional_title="Python Developer",
        contact=ContactInfo(email="ana@example.com"),
        unclassified_text=["Ana Garcia", "Python Developer"],
    )

    assert result["personal_data"]["full_name"] == "Ana Garcia"
    assert result["contact"]["email"] == "ana@example.com"
    assert result["education"] == []
    assert result["metadata"]["processed_successfully"] is True
