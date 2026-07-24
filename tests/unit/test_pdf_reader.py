from pathlib import Path

import pytest

from cv_analyzer.exceptions import InvalidFileTypeError
from cv_analyzer.pdf_reader import validate_pdf_file


def test_validate_pdf_file_rejects_non_pdf_extension(tmp_path: Path) -> None:
    file_path = tmp_path / "cv.txt"
    file_path.write_text("contenido", encoding="utf-8")

    with pytest.raises(InvalidFileTypeError):
        validate_pdf_file(file_path)


def test_validate_pdf_file_rejects_missing_file(tmp_path: Path) -> None:
    file_path = tmp_path / "missing.pdf"

    with pytest.raises(FileNotFoundError):
        validate_pdf_file(file_path)

