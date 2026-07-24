import json

import pytest

from cv_analyzer.ui_helpers import build_download_name, format_file_size
from cv_analyzer.ui_helpers import serialize_cv_result
from cv_analyzer.ui_helpers import temporary_uploaded_pdf


def test_temporary_uploaded_pdf_is_safe_and_removed() -> None:
    content = b"%PDF-1.7 example"

    with temporary_uploaded_pdf(content, "../../private.pdf") as file_path:
        temporary_directory = file_path.parent
        assert file_path.name == "private.pdf"
        assert file_path.read_bytes() == content

    assert not file_path.exists()
    assert not temporary_directory.exists()


def test_temporary_uploaded_pdf_replaces_invalid_windows_characters() -> None:
    with temporary_uploaded_pdf(b"pdf", r"C:\docs\cv:2026?.pdf") as file_path:
        assert file_path.name == "cv_2026_.pdf"


def test_temporary_uploaded_pdf_is_removed_after_exception() -> None:
    with pytest.raises(RuntimeError):
        with temporary_uploaded_pdf(b"pdf", "cv.pdf") as file_path:
            temporary_directory = file_path.parent
            raise RuntimeError("processing failed")

    assert not temporary_directory.exists()


def test_serialize_cv_result_preserves_unicode_and_is_valid_json() -> None:
    result: dict[str, object] = {
        "personal_data": {"full_name": "José García"},
    }

    serialized_result = serialize_cv_result(result)

    assert serialized_result.endswith("\n")
    assert "José García" in serialized_result
    assert json.loads(serialized_result) == result


@pytest.mark.parametrize(
    ("source_file", "expected_name"),
    [
        ("ana.pdf", "ana_analizado.json"),
        ("cv.final.pdf", "cv.final_analizado.json"),
        ("../../private.pdf", "private_analizado.json"),
        (None, "curriculum_analizado.json"),
    ],
)
def test_build_download_name(
    source_file: object,
    expected_name: str,
) -> None:
    assert build_download_name(source_file) == expected_name


@pytest.mark.parametrize(
    ("size_bytes", "expected_label"),
    [
        (None, "No disponible"),
        (512, "512 B"),
        (1024, "1.0 KB"),
        (1024 * 1024, "1.0 MB"),
    ],
)
def test_format_file_size(
    size_bytes: int | None,
    expected_label: str,
) -> None:
    assert format_file_size(size_bytes) == expected_label
