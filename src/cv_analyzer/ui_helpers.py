"""
Helpers independientes de Streamlit para la capa de presentacion.

Gestionan el archivo temporal subido, la serializacion descargable y formatos
visuales simples. No realizan extraccion ni interpretacion del curriculum.
"""

from collections.abc import Iterator
from contextlib import contextmanager
import json
from pathlib import Path
import re
from tempfile import TemporaryDirectory


DEFAULT_UPLOAD_NAME = "curriculum.pdf"
DEFAULT_DOWNLOAD_STEM = "curriculum"
INVALID_FILE_NAME_PATTERN = re.compile(r'[<>:"/\\|?*\x00-\x1F]')
WINDOWS_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{index}" for index in range(1, 10)),
    *(f"LPT{index}" for index in range(1, 10)),
}


@contextmanager
def temporary_uploaded_pdf(
    content: bytes,
    original_name: str,
) -> Iterator[Path]:
    """
    Guarda una carga en un directorio temporal y elimina todo al finalizar.

    Args:
        content: Contenido binario recibido por la interfaz.
        original_name: Nombre original informado por el navegador.

    Yields:
        Ruta temporal con un nombre de archivo seguro.
    """
    safe_name = _safe_file_name(original_name)

    with TemporaryDirectory(prefix="cv-analyzer-") as temporary_directory:
        temporary_path = Path(temporary_directory) / safe_name
        temporary_path.write_bytes(content)
        yield temporary_path


def serialize_cv_result(result: dict[str, object]) -> str:
    """
    Serializa el resultado como JSON legible y compatible con Unicode.

    Args:
        result: Salida estructurada del pipeline.

    Returns:
        Documento JSON terminado en salto de linea.
    """
    return f"{json.dumps(result, ensure_ascii=False, indent=2)}\n"


def build_download_name(source_file: object) -> str:
    """
    Construye un nombre estable para la descarga del resultado.

    Args:
        source_file: Nombre de origen almacenado en metadata.

    Returns:
        Nombre terminado en `_analizado.json`.
    """
    if isinstance(source_file, str):
        safe_name = _safe_file_name(source_file)
        stem = Path(safe_name).stem
    else:
        stem = DEFAULT_DOWNLOAD_STEM

    return f"{stem or DEFAULT_DOWNLOAD_STEM}_analizado.json"


def format_file_size(size_bytes: int | None) -> str:
    """
    Convierte bytes en una etiqueta compacta para la interfaz.

    Args:
        size_bytes: Tamano del archivo o None.

    Returns:
        Tamano formateado con B, KB o MB.
    """
    if size_bytes is None or size_bytes < 0:
        return "No disponible"
    if size_bytes < 1024:
        return f"{size_bytes} B"
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes / (1024 * 1024):.1f} MB"


def _safe_file_name(original_name: str) -> str:
    normalized_name = original_name.replace("\\", "/")
    candidate = normalized_name.rsplit("/", maxsplit=1)[-1].strip()
    candidate = INVALID_FILE_NAME_PATTERN.sub("_", candidate).rstrip(" .")

    if candidate in {"", ".", ".."}:
        return DEFAULT_UPLOAD_NAME
    if Path(candidate).stem.upper() in WINDOWS_RESERVED_NAMES:
        return f"_{candidate}"

    return candidate
