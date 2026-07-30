from pathlib import Path

import fitz
import pytest

from cv_analyzer.constants import PDF_EMPTY_FILE_MESSAGE, PDF_NO_PAGES_MESSAGE
from cv_analyzer.constants import PDF_EMPTY_PAGES_WARNING_TEMPLATE
from cv_analyzer.constants import PDF_SCANNED_MESSAGE
from cv_analyzer.constants import PDF_SCANNED_PAGES_WARNING_TEMPLATE
from cv_analyzer.exceptions import EmptyDocumentError, FileTooLargeError
from cv_analyzer.exceptions import InvalidFileTypeError, PDFReadError
from cv_analyzer.exceptions import PasswordProtectedPDFError
from cv_analyzer.exceptions import ProtectedPDFError, ScannedPDFError
from cv_analyzer.pdf_reader import (
    extract_text_from_pdf,
    read_pdf_text,
    validate_pdf_file,
)
from tests.fixtures.pdf_factory import create_encrypted_pdf
from tests.fixtures.pdf_factory import create_image_only_pdf
from tests.fixtures.pdf_factory import create_partially_scanned_pdf
from tests.fixtures.pdf_factory import create_text_pdf


def test_validate_pdf_file_rejects_non_pdf_extension(tmp_path: Path) -> None:
    file_path = tmp_path / "cv.txt"
    file_path.write_text("contenido", encoding="utf-8")

    with pytest.raises(InvalidFileTypeError):
        validate_pdf_file(file_path)


def test_validate_pdf_file_rejects_missing_file(tmp_path: Path) -> None:
    file_path = tmp_path / "missing.pdf"

    with pytest.raises(FileNotFoundError) as error:
        validate_pdf_file(file_path)

    assert str(file_path) not in str(error.value)


def test_validate_pdf_file_rejects_directory(tmp_path: Path) -> None:
    with pytest.raises(IsADirectoryError) as error:
        validate_pdf_file(tmp_path)

    assert str(tmp_path) not in str(error.value)


def test_validate_pdf_file_rejects_zero_byte_file(tmp_path: Path) -> None:
    file_path = tmp_path / "empty-file.pdf"
    file_path.touch()

    with pytest.raises(EmptyDocumentError, match=PDF_EMPTY_FILE_MESSAGE):
        validate_pdf_file(file_path)


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


def test_read_pdf_text_rejects_document_without_pages(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class PageLessDocument:
        needs_pass = False
        page_count = 0

        def __enter__(self) -> "PageLessDocument":
            return self

        def __exit__(self, *args: object) -> None:
            return None

    file_path = tmp_path / "no-pages.pdf"
    file_path.write_bytes(b"%PDF synthetic")
    monkeypatch.setattr(
        "cv_analyzer.pdf_reader.fitz.open",
        lambda _: PageLessDocument(),
    )

    with pytest.raises(EmptyDocumentError, match=PDF_NO_PAGES_MESSAGE):
        read_pdf_text(file_path)


def test_read_pdf_text_identifies_image_only_pdf(tmp_path: Path) -> None:
    file_path = create_image_only_pdf(tmp_path / "scanned.pdf")

    with pytest.raises(ScannedPDFError, match=PDF_SCANNED_MESSAGE):
        read_pdf_text(file_path)


def test_read_pdf_text_warns_about_partially_scanned_pdf(
    tmp_path: Path,
) -> None:
    file_path = create_partially_scanned_pdf(tmp_path / "partial-scan.pdf")

    result = read_pdf_text(file_path)

    assert result.text == "Synthetic CV with text"
    assert result.page_count == 2
    assert result.warnings == [
        PDF_SCANNED_PAGES_WARNING_TEMPLATE.format(pages="2")
    ]


def test_read_pdf_text_warns_about_empty_page_in_textual_pdf(
    tmp_path: Path,
) -> None:
    file_path = create_text_pdf(
        tmp_path / "partial-empty.pdf",
        ["Synthetic CV with text", ""],
    )

    result = read_pdf_text(file_path)

    assert result.text == "Synthetic CV with text"
    assert result.page_count == 2
    assert result.warnings == [
        PDF_EMPTY_PAGES_WARNING_TEMPLATE.format(pages="2")
    ]


def test_read_pdf_text_wraps_invalid_pdf_content(tmp_path: Path) -> None:
    file_path = tmp_path / "broken.pdf"
    file_path.write_text("esto no es un pdf real", encoding="utf-8")

    with pytest.raises(PDFReadError) as error:
        read_pdf_text(file_path)

    assert error.value.__cause__ is not None


def test_read_pdf_text_rejects_encrypted_pdf(tmp_path: Path) -> None:
    file_path = create_encrypted_pdf(tmp_path / "protected.pdf")

    with pytest.raises(PasswordProtectedPDFError) as error:
        read_pdf_text(file_path)

    assert isinstance(error.value, ProtectedPDFError)
