"""
Modulo encargado de detectar secciones principales de un curriculum.

Divide lineas limpias en bloques segun encabezados conocidos en espanol e
ingles. Admite decoracion, numeracion y variantes bilingues conservadoras.
Conserva el texto previo al primer encabezado y cualquier contenido que no
pueda asignarse con certeza.

No extrae datos estructurados de cada seccion ni normaliza fechas.
"""

from collections.abc import Iterable
from dataclasses import dataclass, field
import re
import unicodedata


# Retira numeraciones habituales como `1.`, `2 -` o `IV)` despues de eliminar
# la decoracion exterior. No elimina numeros sin delimitador.
HEADING_NUMBER_PREFIX_PATTERN = re.compile(
    r"^(?:\d+(?:\.\d+)*|[ivxlcdm]+)\s*[.)-]\s*",
    re.IGNORECASE,
)

# Separa encabezados bilingues o equivalentes escritos con barra, tuberia o
# parentesis. Todas las partes deben ser aliases conocidos para aceptar la
# linea como encabezado.
HEADING_VARIANT_SEPARATOR_PATTERN = re.compile(r"\s*(?:/|\||\(|\))\s*")

# Separa un encabezado de contenido escrito en la misma linea. Los guiones y
# tuberias requieren espacios para no confundir URLs o nombres compuestos.
INLINE_HEADING_SEPARATOR_PATTERN = re.compile(
    r":|\s+(?:-|\u2013|\u2014|\|)\s+"
)


SECTION_ALIASES: dict[str, set[str]] = {
    "profile": {
        "acerca de mi",
        "extracto profesional",
        "objetivo profesional",
        "perfil",
        "perfil profesional",
        "resumen",
        "sobre mi",
        "about me",
        "career objective",
        "professional summary",
        "summary",
        "profile",
        "professional profile",
    },
    "experience": {
        "experiencia",
        "experiencia laboral",
        "experiencia profesional",
        "experiencia relevante",
        "historial laboral",
        "trayectoria profesional",
        "career history",
        "experience",
        "relevant experience",
        "work history",
        "work experience",
        "professional experience",
        "employment history",
    },
    "education": {
        "antecedentes academicos",
        "formacion",
        "formacion academica",
        "formacion reglada",
        "formacion y estudios",
        "educacion y formacion",
        "educacion",
        "estudios",
        "estudios academicos",
        "historial academico",
        "titulaciones",
        "academic education",
        "education",
        "academic background",
        "academic qualifications",
        "educational background",
        "qualifications",
    },
    "skills": {
        "habilidades",
        "habilidades tecnicas",
        "competencias",
        "competencias clave",
        "competencias profesionales",
        "competencias tecnicas",
        "conocimientos",
        "conocimientos tecnicos",
        "tecnologias",
        "tecnologias y herramientas",
        "herramientas y tecnologias",
        "stack tecnologico",
        "aptitudes",
        "core competencies",
        "hard skills",
        "skills",
        "skills and tools",
        "tech stack",
        "technical skills",
        "technical competencies",
        "competencies",
        "tools",
    },
    "languages": {
        "idiomas",
        "idiomas y nivel",
        "conocimientos de idiomas",
        "competencias linguisticas",
        "lenguas",
        "foreign languages",
        "language skills",
        "language proficiency",
        "languages",
    },
    "certifications": {
        "acreditaciones",
        "certificaciones",
        "certificaciones y licencias",
        "certificados",
        "certificados y acreditaciones",
        "credenciales",
        "licencias y certificaciones",
        "certifications",
        "certificates",
        "credentials",
        "licenses",
        "licenses and certifications",
        "licenses certifications",
    },
    "courses": {
        "capacitacion",
        "cursos",
        "cursos y formacion",
        "cursos y seminarios",
        "cursos and formacion",
        "formacion adicional",
        "formacion complementaria",
        "seminarios",
        "talleres",
        "additional training",
        "continuing education",
        "courses and training",
        "courses",
        "professional development",
        "training",
    },
    "projects": {
        "proyectos",
        "proyectos destacados",
        "proyectos personales",
        "featured projects",
        "project experience",
        "projects",
        "personal projects",
    },
}

SECTION_BY_ALIAS = {
    alias: section_name
    for section_name, aliases in SECTION_ALIASES.items()
    for alias in aliases
}


@dataclass(frozen=True)
class SectionDetectionResult:
    """
    Resultado de la deteccion de secciones.

    Args:
        sections: Diccionario con las lineas agrupadas por seccion.
        warnings: Advertencias tecnicas no bloqueantes.
        section_order: Secciones reconocidas en su orden de aparicion,
            incluidas las repeticiones.
    """

    sections: dict[str, list[str]]
    warnings: list[str]
    section_order: list[str] = field(default_factory=list)


def normalize_heading(text: str) -> str:
    """
    Normaliza un posible encabezado antes de compararlo.

    Convierte el texto a minusculas, normaliza acentos, elimina decoracion
    exterior y retira prefijos numericos. Asi se consideran equivalentes
    encabezados como "Experiencia", "1. EXPERIENCIA:" y "• Experiencia •".

    Args:
        text: Linea que podria representar un encabezado.

    Returns:
        Encabezado normalizado.
    """
    lowered_text = text.strip().casefold().replace("&", " and ")
    decomposed_text = unicodedata.normalize("NFD", lowered_text)
    accentless_text = "".join(
        character
        for character in decomposed_text
        if unicodedata.category(character) != "Mn"
    )
    collapsed_text = " ".join(accentless_text.split())
    undecorated_text = _strip_edge_decoration(collapsed_text)
    unnumbered_text = HEADING_NUMBER_PREFIX_PATTERN.sub(
        "",
        undecorated_text,
        count=1,
    )
    return _strip_edge_decoration(unnumbered_text)


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
    candidates, _ = _analyze_section_line(line)
    return next(iter(candidates)) if len(candidates) == 1 else None


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
    section_order: list[str] = []
    current_section = "unclassified"
    seen_sections: set[str] = set()

    for line in lines:
        section_candidates, inline_content = _analyze_section_line(line)
        detected_section = (
            next(iter(section_candidates))
            if len(section_candidates) == 1
            else None
        )

        if detected_section is not None:
            if detected_section in seen_sections:
                warnings.append(
                    f"Seccion duplicada detectada: {detected_section}."
                )
            seen_sections.add(detected_section)
            section_order.append(detected_section)
            current_section = detected_section
            sections.setdefault(current_section, [])
            if inline_content:
                sections[current_section].append(inline_content)
            continue

        if len(section_candidates) > 1:
            warnings.append(
                "Encabezado ambiguo conservado sin clasificar: "
                f"{normalize_heading(line)}."
            )
            current_section = "unclassified"
            sections[current_section].append(line)
            continue

        # Conservamos cualquier contenido no reconocido para evitar perdidas
        # silenciosas durante el procesamiento del curriculum.
        sections.setdefault(current_section, []).append(line)

    return SectionDetectionResult(
        sections=sections,
        warnings=warnings,
        section_order=section_order,
    )


def _find_section_candidates(line: str) -> set[str]:
    normalized_line = normalize_heading(line)
    direct_match = SECTION_BY_ALIAS.get(normalized_line)
    if direct_match is not None:
        return {direct_match}

    variants = [
        variant
        for variant in HEADING_VARIANT_SEPARATOR_PATTERN.split(
            normalized_line
        )
        if variant
    ]
    if len(variants) < 2:
        return set()

    matches = [SECTION_BY_ALIAS.get(variant) for variant in variants]
    if any(match is None for match in matches):
        return set()

    return {match for match in matches if match is not None}


def _analyze_section_line(line: str) -> tuple[set[str], str | None]:
    direct_candidates = _find_section_candidates(line)
    if direct_candidates:
        return direct_candidates, None

    separators = list(INLINE_HEADING_SEPARATOR_PATTERN.finditer(line))
    for separator in reversed(separators):
        heading = line[: separator.start()].strip()
        content = line[separator.end() :].strip()
        if not heading or not content:
            continue
        candidates = _find_section_candidates(heading)
        if candidates:
            return candidates, content

    return set(), None


def _strip_edge_decoration(text: str) -> str:
    start_index = 0
    end_index = len(text)

    while start_index < end_index and not text[start_index].isalnum():
        start_index += 1
    while end_index > start_index and not text[end_index - 1].isalnum():
        end_index -= 1

    return text[start_index:end_index].strip()
