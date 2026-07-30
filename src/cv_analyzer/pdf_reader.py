"""
Modulo encargado de leer y validar documentos PDF.

Contiene funciones relacionadas con la validacion del archivo, apertura del
documento, conteo de paginas, extraccion de texto y deteccion conservadora de
paginas posiblemente escaneadas.

No clasifica secciones ni interpreta datos personales.
"""

from dataclasses import dataclass, field
from pathlib import Path

import fitz

from cv_analyzer.config import MAX_FILE_SIZE_BYTES
from cv_analyzer.constants import ALLOWED_PDF_EXTENSION, PDF_EMPTY_FILE_MESSAGE
from cv_analyzer.constants import FILE_IS_DIRECTORY_MESSAGE
from cv_analyzer.constants import FILE_NOT_FOUND_MESSAGE
from cv_analyzer.constants import PDF_EMPTY_PAGES_WARNING_TEMPLATE
from cv_analyzer.constants import PDF_EMPTY_TEXT_MESSAGE, PDF_NO_PAGES_MESSAGE
from cv_analyzer.constants import PDF_PROTECTED_MESSAGE, PDF_SCANNED_MESSAGE
from cv_analyzer.constants import PDF_SCANNED_PAGES_WARNING_TEMPLATE
from cv_analyzer.exceptions import EmptyDocumentError, FileTooLargeError
from cv_analyzer.exceptions import InvalidFileTypeError, PDFReadError
from cv_analyzer.exceptions import PasswordProtectedPDFError, ScannedPDFError


@dataclass(frozen=True)
class PDFTextExtractionResult:
    """
    Resultado tecnico de la lectura de un PDF.

    Args:
        text: Texto extraido del documento.
        page_count: Numero de paginas detectadas.
        file_size_bytes: Tamano del archivo procesado.
        warnings: Advertencias tecnicas no bloqueantes.
    """

    text: str
    page_count: int
    file_size_bytes: int
    warnings: list[str]
    embedded_links: list[str] = field(default_factory=list)


def validate_pdf_file(file_path: Path) -> None:
    """
    Valida que la ruta recibida apunte a un archivo PDF existente.

    Args:
        file_path: Ruta del documento que debe validarse.

    Raises:
        FileNotFoundError: Si la ruta no existe.
        IsADirectoryError: Si la ruta apunta a un directorio.
        InvalidFileTypeError: Si el archivo no tiene extension PDF.
        EmptyDocumentError: Si el archivo no contiene ningun byte.
        FileTooLargeError: Si el archivo supera el tamano maximo configurado.
    """
    if not file_path.exists():
        raise FileNotFoundError(FILE_NOT_FOUND_MESSAGE)

    if not file_path.is_file():
        raise IsADirectoryError(FILE_IS_DIRECTORY_MESSAGE)

    if file_path.suffix.lower() != ALLOWED_PDF_EXTENSION:
        raise InvalidFileTypeError("El archivo debe tener extension PDF.")

    file_size_bytes = file_path.stat().st_size
    if file_size_bytes == 0:
        raise EmptyDocumentError(PDF_EMPTY_FILE_MESSAGE)

    if file_size_bytes > MAX_FILE_SIZE_BYTES:
        raise FileTooLargeError("El archivo supera el tamano maximo permitido.")


def read_pdf_text(file_path: Path) -> PDFTextExtractionResult:
    """
    Lee un PDF y devuelve texto junto con metadatos tecnicos basicos.

    Args:
        file_path: Ruta del documento que debe procesarse.

    Returns:
        Resultado con texto, numero de paginas, tamano y advertencias.

    Raises:
        FileNotFoundError: Si la ruta no existe.
        IsADirectoryError: Si la ruta apunta a un directorio.
        InvalidFileTypeError: Si el archivo no tiene extension PDF.
        FileTooLargeError: Si el archivo supera el tamano maximo configurado.
        PasswordProtectedPDFError: Si el PDF requiere contraseña.
        ScannedPDFError: Si parece contener solo imagenes sin texto.
        EmptyDocumentError: Si el archivo esta vacio, no tiene paginas o no
            contiene texto extraible.
        PDFReadError: Si el documento no puede abrirse o leerse.
    """
    validate_pdf_file(file_path)
    file_size_bytes = file_path.stat().st_size

    try:
        with fitz.open(file_path) as document:
            if document.needs_pass:
                raise PasswordProtectedPDFError(PDF_PROTECTED_MESSAGE)

            page_count = document.page_count
            if page_count == 0:
                raise EmptyDocumentError(PDF_NO_PAGES_MESSAGE)

            page_texts, page_has_images, embedded_links = (
                _extract_document_pages(document)
            )
    except (PasswordProtectedPDFError, EmptyDocumentError):
        raise
    except Exception as error:
        raise PDFReadError("No se pudo leer el documento PDF.") from error

    extracted_text = "\n".join(page_texts).strip()

    if not extracted_text:
        if any(page_has_images):
            raise ScannedPDFError(PDF_SCANNED_MESSAGE)
        raise EmptyDocumentError(PDF_EMPTY_TEXT_MESSAGE)

    return PDFTextExtractionResult(
        text=extracted_text,
        page_count=page_count,
        file_size_bytes=file_size_bytes,
        warnings=_build_page_warnings(page_texts, page_has_images),
        embedded_links=embedded_links,
    )


def extract_text_from_pdf(file_path: Path) -> str:
    """
    Extrae el contenido textual de un documento PDF.

    Args:
        file_path: Ruta del documento que debe procesarse.

    Returns:
        Texto extraido de todas las paginas con saltos de linea entre paginas.

    Raises:
        FileNotFoundError: Si la ruta no existe.
        InvalidFileTypeError: Si el archivo no tiene extension PDF.
        PasswordProtectedPDFError: Si el PDF requiere contraseña.
        ScannedPDFError: Si parece contener solo imagenes sin texto.
        EmptyDocumentError: Si el PDF no contiene texto extraible.
        PDFReadError: Si el documento no puede abrirse o leerse.
    """
    return read_pdf_text(file_path).text


def _extract_document_pages(
    document: fitz.Document,
) -> tuple[list[str], list[bool], list[str]]:
    page_texts: list[str] = []
    page_has_images: list[bool] = []
    embedded_links: list[str] = []
    seen_links: set[str] = set()

    for page in document:
        page_text = page.get_text("text")
        page_texts.append(page_text)
        page_has_images.append(bool(page.get_images(full=True)))
        for uri in _extract_page_link_uris(page, page_text):
            normalized_uri = uri.casefold()
            if normalized_uri not in seen_links:
                seen_links.add(normalized_uri)
                embedded_links.append(uri)

    return page_texts, page_has_images, embedded_links


def _extract_page_link_uris(page: fitz.Page, page_text: str) -> list[str]:
    """Recupera hipervinculos web ocultos tras texto o iconos del PDF."""
    known_text = page_text.casefold()
    seen_uris: set[str] = set()
    uris: list[str] = []

    for link in page.get_links():
        uri = link.get("uri")
        if not isinstance(uri, str):
            continue
        cleaned_uri = uri.strip()
        normalized_uri = cleaned_uri.casefold()
        if (
            not normalized_uri.startswith(("http://", "https://"))
            or normalized_uri in known_text
            or normalized_uri in seen_uris
        ):
            continue
        seen_uris.add(normalized_uri)
        uris.append(cleaned_uri)

    return uris


def _build_page_warnings(
    page_texts: list[str],
    page_has_images: list[bool],
) -> list[str]:
    scanned_pages: list[str] = []
    empty_pages: list[str] = []

    for page_number, (page_text, has_images) in enumerate(
        zip(page_texts, page_has_images, strict=True),
        start=1,
    ):
        if page_text.strip():
            continue
        if has_images:
            scanned_pages.append(str(page_number))
        else:
            empty_pages.append(str(page_number))

    warnings: list[str] = []
    if scanned_pages:
        warnings.append(
            PDF_SCANNED_PAGES_WARNING_TEMPLATE.format(
                pages=", ".join(scanned_pages)
            )
        )
    if empty_pages:
        warnings.append(
            PDF_EMPTY_PAGES_WARNING_TEMPLATE.format(
                pages=", ".join(empty_pages)
            )
        )
    return warnings
