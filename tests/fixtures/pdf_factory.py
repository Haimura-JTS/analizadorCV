"""Construccion de PDFs sinteticos para pruebas sin datos personales reales."""

from collections.abc import Sequence
from pathlib import Path

import fitz


def create_text_pdf(file_path: Path, pages: Sequence[str]) -> Path:
    """Crea un PDF con texto extraible y una pagina por bloque recibido."""
    document = fitz.open()
    try:
        for page_text in pages:
            page = document.new_page()
            for line_number, line in enumerate(page_text.splitlines()):
                y_position = 72 + (line_number * 16)
                page.insert_text((72, y_position), line, fontsize=11)
        document.save(file_path)
    finally:
        document.close()

    return file_path


def create_two_column_text_pdf(
    file_path: Path,
    left_text: str,
    right_text: str,
) -> Path:
    """Crea un PDF textual con dos bloques posicionados como columnas."""
    document = fitz.open()
    try:
        page = document.new_page()
        left_space = page.insert_textbox(
            fitz.Rect(48, 54, 275, 788),
            left_text,
            fontsize=10.5,
        )
        right_space = page.insert_textbox(
            fitz.Rect(320, 54, 547, 788),
            right_text,
            fontsize=10.5,
        )
        if left_space < 0 or right_space < 0:
            raise ValueError("El contenido sintetico no cabe en las columnas.")
        document.save(file_path)
    finally:
        document.close()

    return file_path


def create_blank_pdf(file_path: Path) -> Path:
    """Crea un PDF valido sin texto extraible."""
    document = fitz.open()
    try:
        document.new_page()
        document.save(file_path)
    finally:
        document.close()

    return file_path


def create_image_only_pdf(file_path: Path) -> Path:
    """Crea un PDF valido con una imagen y sin capa de texto."""
    document = fitz.open()
    try:
        page = document.new_page()
        _insert_test_image(page)
        document.save(file_path)
    finally:
        document.close()

    return file_path


def create_partially_scanned_pdf(file_path: Path) -> Path:
    """Crea un PDF con una pagina textual y otra basada en imagen."""
    document = fitz.open()
    try:
        text_page = document.new_page()
        text_page.insert_text((72, 72), "Synthetic CV with text")
        image_page = document.new_page()
        _insert_test_image(image_page)
        document.save(file_path)
    finally:
        document.close()

    return file_path


def create_encrypted_pdf(file_path: Path) -> Path:
    """Crea un PDF que requiere contrasena para abrir su contenido."""
    document = fitz.open()
    try:
        page = document.new_page()
        page.insert_text((72, 72), "Protected synthetic CV")
        document.save(
            file_path,
            encryption=fitz.PDF_ENCRYPT_AES_256,
            owner_pw="owner-password",
            user_pw="user-password",
        )
    finally:
        document.close()

    return file_path


def _insert_test_image(page: fitz.Page) -> None:
    pixmap = fitz.Pixmap(
        fitz.csRGB,
        fitz.IRect(0, 0, 16, 16),
        False,
    )
    pixmap.clear_with(220)
    page.insert_image(
        fitz.Rect(72, 72, 144, 144),
        pixmap=pixmap,
    )
