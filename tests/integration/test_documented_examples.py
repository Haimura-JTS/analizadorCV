import json
from pathlib import Path

from cv_analyzer.models import CVResultModel
from examples.run_example import run_example


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_documented_reference_result_matches_the_schema() -> None:
    reference_path = PROJECT_ROOT / "examples" / "example_result.json"
    result = json.loads(reference_path.read_text(encoding="utf-8"))

    CVResultModel.model_validate(result)
    assert result["metadata"]["processed_successfully"] is True
    assert result["personal_data"]["full_name"] == "Alex Ejemplo"


def test_documented_example_runs_and_writes_valid_json(
    tmp_path: Path,
) -> None:
    output_path = tmp_path / "sample_result.json"

    result = run_example(output_path)
    written_result = json.loads(output_path.read_text(encoding="utf-8"))

    CVResultModel.model_validate(result)
    assert written_result == result
    assert result["metadata"]["processed_successfully"] is True
    assert result["metadata"]["source_file"] == "sample_cv.pdf"
