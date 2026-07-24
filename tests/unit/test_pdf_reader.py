from pathlib import Path

import fitz
import pytest

from cv_analyzer.exceptions import EmptyDocumentError, FileTooLargeError
from cv_analyzer.exceptions import InvalidFileTypeError, PDFReadError
from cv_analyzer.exceptions import ProtectedPDFError
from cv_analyzer.pdf_reader import extract_text_from_pdf, read_pdf_text, validate_pdf_file
from tests.fixtures.pdf_factory import create_encrypted_pdf


def test_validate_pdf_file_rejects_non_pdf_extension(tmp_path: Path) -> None:
    file_path = tmp_path / "cv.txt"
    file_path.write_text("contenido", encoding="utf-8")

    with pytest.raises(InvalidFileTypeError):
        validate_pdf_file(file_path)


def test_validate_pdf_file_rejects_missing_file(tmp_path: Path) -> None:
    file_path = tmp_path / "missing.pdf"

    with pytest.raises(FileNotFoundError):
        validate_pdf_file(file_path)


def test_validate_pdf_file_rejects_directory(tmp_path: Path) -> None:
    with pytest.raises(IsADirectoryError):
        validate_pdf_file(tmp_path)


def test_validate_pdf_file_rejects_file_that_is_too_large(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    file_path = tmp_path / "cv.pdf"
    file_path.write_bytes(b"%PDF")
    monkeypatch.setattr("cv_analyzer.pdf_reader.MAX_FILE_SIZE_BYTES", 1)

    with pytest.raises(FileTooLargeError):
        validate_pdf_file(file_path)


def test_read_pdf_text_returns_text_and_metadata(tmp_path: Path) -> None:
    file_path = tmp_path / "cv.pdf"
    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), "Experiencia profesional")
    document.save(file_path)
    document.close()

    result = read_pdf_text(file_path)

    assert "Experiencia profesional" in result.text
    assert result.page_count == 1
    assert result.file_size_bytes > 0
    assert result.warnings == []


def test_extract_text_from_pdf_preserves_string_interface(tmp_path: Path) -> None:
    file_path = tmp_path / "cv.pdf"
    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), "Formacion academica")
    document.save(file_path)
    document.close()

    assert extract_text_from_pdf(file_path) == "Formacion academica"


def test_read_pdf_text_rejects_empty_pdf(tmp_path: Path) -> None:
    file_path = tmp_path / "empty.pdf"
    document = fitz.open()
    document.new_page()
    document.save(file_path)
    document.close()

    with pytest.raises(EmptyDocumentError):
        read_pdf_text(file_path)


def test_read_pdf_text_wraps_invalid_pdf_content(tmp_path: Path) -> None:
    file_path = tmp_path / "broken.pdf"
    file_path.write_text("esto no es un pdf real", encoding="utf-8")

    with pytest.raises(PDFReadError):
        read_pdf_text(file_path)


def test_read_pdf_text_rejects_encrypted_pdf(tmp_path: Path) -> None:
    file_path = create_encrypted_pdf(tmp_path / "protected.pdf")

    with pytest.raises(ProtectedPDFError):
        read_pdf_text(file_path)
