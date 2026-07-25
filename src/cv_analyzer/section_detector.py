"""
Modulo encargado de detectar secciones principales de un curriculum.

Divide lineas limpias en bloques segun encabezados conocidos en espanol e
ingles. Conserva el texto previo al primer encabezado y cualquier contenido
no interpretable dentro de la seccion activa.

No extrae datos estructurados de cada seccion ni normaliza fechas.
"""

from collections.abc import Iterable
from dataclasses import dataclass
import unicodedata


SECTION_ALIASES: dict[str, set[str]] = {
    "profile": {
        "perfil",
        "perfil profesional",
        "resumen",
        "sobre mi",
        "summary",
        "profile",
        "professional profile",
    },
    "experience": {
        "experiencia",
        "experiencia laboral",
        "experiencia profesional",
        "historial laboral",
        "experience",
        "work experience",
        "professional experience",
        "employment history",
    },
    "education": {
        "formacion",
        "formacion academica",
        "educacion",
        "estudios",
        "education",
        "academic background",
    },
    "skills": {
        "habilidades",
        "competencias",
        "aptitudes",
        "skills",
        "technical skills",
        "competencies",
    },
    "languages": {
        "idiomas",
        "languages",
    },
    "certifications": {
        "certificaciones",
        "certificados",
        "certifications",
        "certificates",
    },
    "courses": {
        "cursos",
        "formacion complementaria",
        "additional training",
        "courses",
    },
    "projects": {
        "proyectos",
        "projects",
        "personal projects",
    },
}


@dataclass(frozen=True)
class SectionDetectionResult:
    """
    Resultado de la deteccion de secciones.

    Args:
        sections: Diccionario con las lineas agrupadas por seccion.
        warnings: Advertencias tecnicas no bloqueantes.
    """

    sections: dict[str, list[str]]
    warnings: list[str]


def normalize_heading(text: str) -> str:
    """
    Normaliza un posible encabezado antes de compararlo.

    Convierte el texto a minusculas, elimina espacios exteriores, retira dos
    puntos finales y normaliza acentos. Asi se consideran equivalentes
    encabezados como "Experiencia", "EXPERIENCIA:" y " experiencia ".

    Args:
        text: Linea que podria representar un encabezado.

    Returns:
        Encabezado normalizado.
    """
    stripped_text = text.strip().lower().removesuffix(":").strip()
    decomposed_text = unicodedata.normalize("NFD", stripped_text)
    return "".join(
        character
        for character in decomposed_text
        if unicodedata.category(character) != "Mn"
    )


def find_section_name(line: str) -> str | None:
    """
    Devuelve el identificador interno asociado a un encabezado.

    La funcion compara la linea normalizada con variantes conocidas. No utiliza
    coincidencias parciales para evitar que frases como "Tengo experiencia con
    Python" sean interpretadas como encabezados.

    Args:
        line: Linea limpia extraida del curriculum.

    Returns:
        Nombre interno de la seccion o None si la linea no es encabezado.
    """
    normalized_line = normalize_heading(line)

    for section_name, aliases in SECTION_ALIASES.items():
        if normalized_line in aliases:
            return section_name

    return None


def detect_sections(lines: Iterable[str]) -> dict[str, list[str]]:
    """
    Agrupa las lineas del curriculum segun sus encabezados.

    Las lineas anteriores al primer encabezado se almacenan en `unclassified`.
    Si una seccion aparece mas de una vez, su contenido se acumula para no
    perder informacion.

    Args:
        lines: Lineas limpias obtenidas del documento.

    Returns:
        Diccionario que relaciona cada seccion con sus lineas.
    """
    return detect_sections_with_warnings(lines).sections


def detect_sections_with_warnings(
    lines: Iterable[str],
) -> SectionDetectionResult:
    """
    Agrupa lineas y registra advertencias de deteccion.

    Args:
        lines: Lineas limpias obtenidas del documento.

    Returns:
        Resultado con secciones detectadas y advertencias.
    """
    sections: dict[str, list[str]] = {"unclassified": []}
    warnings: list[str] = []
    current_section = "unclassified"
    seen_sections: set[str] = set()

    for line in lines:
        detected_section = find_section_name(line)

        if detected_section is not None:
            if detected_section in seen_sections:
                warnings.append(
                    f"Seccion duplicada detectada: {detected_section}."
                )
            seen_sections.add(detected_section)
            current_section = detected_section
            sections.setdefault(current_section, [])
            continue

        # Conservamos cualquier contenido no reconocido para evitar perdidas
        # silenciosas durante el procesamiento del curriculum.
        sections.setdefault(current_section, []).append(line)

    return SectionDetectionResult(sections=sections, warnings=warnings)
