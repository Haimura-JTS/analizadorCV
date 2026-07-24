"""
Modulo encargado de leer y validar documentos PDF.

Contiene funciones relacionadas con la comprobacion basica del archivo,
apertura del documento, conteo de paginas y extraccion de texto.

No clasifica secciones ni interpreta datos personales.
"""

from pathlib import Path

import fitz

from cv_analyzer.constants import ALLOWED_PDF_EXTENSION, PDF_EMPTY_TEXT_MESSAGE
from cv_analyzer.exceptions import EmptyDocumentError, InvalidFileTypeError, PDFReadError


def validate_pdf_file(file_path: Path) -> None:
    """
    Valida que la ruta recibida apunte a un archivo PDF existente.

    Args:
        file_path: Ruta del documento que debe validarse.

    Raises:
        FileNotFoundError: Si la ruta no existe.
        InvalidFileTypeError: Si el archivo no tiene extension PDF.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"No existe el archivo: {file_path}")

    if file_path.suffix.lower() != ALLOWED_PDF_EXTENSION:
        raise InvalidFileTypeError("El archivo debe tener extension PDF.")


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
        EmptyDocumentError: Si el PDF no contiene texto extraible.
        PDFReadError: Si el documento no puede abrirse o leerse.
    """
    validate_pdf_file(file_path)

    try:
        with fitz.open(file_path) as document:
            page_texts = [page.get_text("text") for page in document]
    except Exception as error:
        raise PDFReadError("No se pudo leer el documento PDF.") from error

    extracted_text = "\n".join(page_texts).strip()

    if not extracted_text:
        raise EmptyDocumentError(PDF_EMPTY_TEXT_MESSAGE)

    return extracted_text

