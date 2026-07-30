import pytest
from pydantic import ValidationError

from cv_analyzer.json_builder import build_basic_cv_result
from cv_analyzer.contact_extractor import ContactInfo
from cv_analyzer.models import CVResultModel


def test_cv_result_model_accepts_basic_result() -> None:
    result = build_basic_cv_result(
        full_name=None,
        professional_title=None,
        contact=ContactInfo(),
        unclassified_text=[],
    )

    model = CVResultModel.model_validate(result)

    assert model.metadata.processing_version == "1.0"
    assert model.skills.technical == []


def test_cv_result_model_rejects_unexpected_fields() -> None:
    result = build_basic_cv_result(
        full_name=None,
        professional_title=None,
        contact=ContactInfo(),
        unclassified_text=[],
    )
    result["unexpected"] = True

    with pytest.raises(ValidationError):
        CVResultModel.model_validate(result)


def test_cv_result_model_rejects_non_normalized_date() -> None:
    result = build_basic_cv_result(
        full_name=None,
        professional_title=None,
        contact=ContactInfo(),
        unclassified_text=[],
    )
    result["experience"] = [{"start_date": "Jan 2024"}]

    with pytest.raises(ValidationError):
        CVResultModel.model_validate(result)


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    [
        ("page_count", -1),
        ("file_size_bytes", -1),
        ("page_count", "1"),
        ("processed_successfully", 1),
    ],
)
def test_cv_result_model_rejects_invalid_metadata_values(
    field_name: str,
    invalid_value: object,
) -> None:
    result = build_basic_cv_result(
        full_name=None,
        professional_title=None,
        contact=ContactInfo(),
        unclassified_text=[],
    )
    result["metadata"][field_name] = invalid_value

    with pytest.raises(ValidationError):
        CVResultModel.model_validate(result)


@pytest.mark.parametrize(
    "processed_at",
    [
        "not-a-date",
        "2026-01-01T00:00:00",
        "2026-01-01T01:00:00+01:00",
    ],
)
def test_cv_result_model_requires_utc_processed_at(
    processed_at: str,
) -> None:
    result = build_basic_cv_result(
        full_name=None,
        professional_title=None,
        contact=ContactInfo(),
        unclassified_text=[],
    )
    result["metadata"]["processed_at"] = processed_at

    with pytest.raises(ValidationError):
        CVResultModel.model_validate(result)


def test_cv_result_model_rejects_invalid_contact_formats() -> None:
    result = build_basic_cv_result(
        full_name=None,
        professional_title=None,
        contact=ContactInfo(
            email="correo-invalido",
            linkedin="linkedin.com/in/demo",
        ),
        unclassified_text=[],
    )

    with pytest.raises(ValidationError):
        CVResultModel.model_validate(result)


def test_cv_result_model_rejects_success_with_errors() -> None:
    result = build_basic_cv_result(
        full_name=None,
        professional_title=None,
        contact=ContactInfo(),
        unclassified_text=[],
    )
    result["metadata"]["errors"] = ["Fallo controlado."]

    with pytest.raises(ValidationError):
        CVResultModel.model_validate(result)
