"""
Modulo encargado de limpiar y normalizar texto extraido de curriculums.

Prepara el contenido para los extractores posteriores mediante reglas simples:
retira caracteres invisibles, normaliza saltos de linea, reduce espacios
repetidos y elimina lineas vacias.

No interpreta datos personales ni clasifica secciones.
"""

import re


# Retira marcas invisibles habituales en texto copiado o extraido de PDF.
# Se eliminan, en vez de sustituirse por espacios, porque tambien pueden
# aparecer dentro de una palabra o una URL.
INVISIBLE_CHARACTER_PATTERN = re.compile(
    r"[\u00AD\u200B-\u200D\u2060\uFEFF]"
)

# Elimina controles que no representan contenido, conservando tabuladores y
# saltos de linea para que la normalizacion posterior mantenga la estructura.
UNSUPPORTED_CONTROL_PATTERN = re.compile(
    r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]"
)


def normalize_whitespace(text: str) -> str:
    """
    Normaliza espacios dentro de cada linea del texto.

    Args:
        text: Texto original extraido del documento.

    Returns:
        Texto con espacios internos reducidos y saltos de linea conservados.
    """
    visible_text = INVISIBLE_CHARACTER_PATTERN.sub("", text)
    visible_text = UNSUPPORTED_CONTROL_PATTERN.sub("", visible_text)
    normalized_lines = [
        " ".join(line.split()) for line in visible_text.splitlines()
    ]
    return "\n".join(normalized_lines).strip()


def split_clean_lines(text: str) -> list[str]:
    """
    Divide el texto en lineas utiles para el analisis.

    Args:
        text: Texto original o previamente normalizado.

    Returns:
        Lista de lineas no vacias, sin espacios exteriores.
    """
    normalized_text = normalize_whitespace(text)
    return [line.strip() for line in normalized_text.splitlines() if line.strip()]


def clean_text(text: str) -> str:
    """
    Limpia el texto del curriculum sin modificar su significado.

    Args:
        text: Texto extraido del PDF.

    Returns:
        Texto normalizado con lineas vacias eliminadas.
    """
    return "\n".join(split_clean_lines(text))
