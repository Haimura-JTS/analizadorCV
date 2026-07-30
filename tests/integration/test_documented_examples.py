import json
from pathlib import Path
import re
import tomllib
from urllib.parse import unquote

from cv_analyzer import __version__
from cv_analyzer.models import CVResultModel
from examples.run_example import run_example


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MARKDOWN_LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


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


def test_relative_documentation_links_resolve() -> None:
    markdown_files = [
        PROJECT_ROOT / "README.md",
        PROJECT_ROOT / "CHANGELOG.md",
        PROJECT_ROOT / "examples" / "README.md",
        *(PROJECT_ROOT / "documentation").rglob("*.md"),
    ]
    missing_links: list[str] = []

    for markdown_file in markdown_files:
        content = markdown_file.read_text(encoding="utf-8")
        for target in MARKDOWN_LINK_PATTERN.findall(content):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            relative_target = unquote(target.split("#", maxsplit=1)[0])
            if not relative_target:
                continue
            resolved_target = (markdown_file.parent / relative_target).resolve()
            if not resolved_target.exists():
                missing_links.append(f"{markdown_file.name}: {target}")

    assert missing_links == []


def test_project_version_matches_package_version() -> None:
    pyproject_content = (PROJECT_ROOT / "pyproject.toml").read_text(
        encoding="utf-8"
    )
    project_metadata = tomllib.loads(pyproject_content)["project"]

    assert project_metadata["version"] == __version__
