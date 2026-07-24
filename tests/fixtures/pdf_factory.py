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


def create_blank_pdf(file_path: Path) -> Path:
    """Crea un PDF valido sin texto extraible."""
    document = fitz.open()
    try:
        document.new_page()
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
