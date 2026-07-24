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

