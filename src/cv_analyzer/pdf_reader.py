"""
Modulo encargado de leer y validar documentos PDF.

Contiene funciones relacionadas con la comprobacion basica del archivo,
apertura del documento, conteo de paginas y extraccion de texto.

No clasifica secciones ni interpreta datos personales.
"""

from dataclasses import dataclass
from pathlib import Path

import fitz

from cv_analyzer.config import MAX_FILE_SIZE_BYTES
from cv_analyzer.constants import ALLOWED_PDF_EXTENSION, PDF_EMPTY_TEXT_MESSAGE
from cv_analyzer.constants import PDF_PROTECTED_MESSAGE
from cv_analyzer.exceptions import EmptyDocumentError, FileTooLargeError
from cv_analyzer.exceptions import InvalidFileTypeError, PDFReadError, ProtectedPDFError


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


def validate_pdf_file(file_path: Path) -> None:
    """
    Valida que la ruta recibida apunte a un archivo PDF existente.

    Args:
        file_path: Ruta del documento que debe validarse.

    Raises:
        FileNotFoundError: Si la ruta no existe.
        IsADirectoryError: Si la ruta apunta a un directorio.
        InvalidFileTypeError: Si el archivo no tiene extension PDF.
        FileTooLargeError: Si el archivo supera el tamano maximo configurado.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"No existe el archivo: {file_path}")

    if not file_path.is_file():
        raise IsADirectoryError(f"La ruta no apunta a un archivo: {file_path}")

    if file_path.suffix.lower() != ALLOWED_PDF_EXTENSION:
        raise InvalidFileTypeError("El archivo debe tener extension PDF.")

    if file_path.stat().st_size > MAX_FILE_SIZE_BYTES:
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
        ProtectedPDFError: Si el PDF requiere contraseña.
        EmptyDocumentError: Si el PDF no contiene texto extraible.
        PDFReadError: Si el documento no puede abrirse o leerse.
    """
    validate_pdf_file(file_path)
    file_size_bytes = file_path.stat().st_size

    try:
        with fitz.open(file_path) as document:
            if document.needs_pass:
                raise ProtectedPDFError(PDF_PROTECTED_MESSAGE)

            page_count = document.page_count
            page_texts = [page.get_text("text") for page in document]
    except ProtectedPDFError:
        raise
    except Exception as error:
        raise PDFReadError("No se pudo leer el documento PDF.") from error

    extracted_text = "\n".join(page_texts).strip()

    if not extracted_text:
        raise EmptyDocumentError(PDF_EMPTY_TEXT_MESSAGE)

    return PDFTextExtractionResult(
        text=extracted_text,
        page_count=page_count,
        file_size_bytes=file_size_bytes,
        warnings=[],
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
        ProtectedPDFError: Si el PDF requiere contraseña.
        EmptyDocumentError: Si el PDF no contiene texto extraible.
        PDFReadError: Si el documento no puede abrirse o leerse.
    """
    return read_pdf_text(file_path).text
