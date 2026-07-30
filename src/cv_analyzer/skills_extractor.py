"""
Extractor y clasificador conservador de habilidades.

Respeta etiquetas explicitas y utiliza listas visibles para distinguir
lenguajes, herramientas y habilidades interpersonales. Los valores no
reconocidos se conservan como habilidades tecnicas.

No calcula niveles de dominio ni infiere habilidades ausentes.
"""

from dataclasses import dataclass

from cv_analyzer.extraction_utils import clean_nonempty_lines
from cv_analyzer.extraction_utils import deduplicate_preserving_order
from cv_analyzer.extraction_utils import is_bullet_line, split_values
from cv_analyzer.extraction_utils import normalize_lookup_text, strip_bullet


SKILL_CATEGORIES = (
    "technical",
    "tools",
    "programming_languages",
    "soft_skills",
)

SKILL_LABELS = {
    "aptitudes tecnicas": "technical",
    "bases de datos": "technical",
    "databases": "technical",
    "frameworks": "technical",
    "technical": "technical",
    "technical skills": "technical",
    "tecnologias": "technical",
    "herramientas": "tools",
    "platforms": "tools",
    "tools": "tools",
    "lenguajes": "programming_languages",
    "lenguajes de programacion": "programming_languages",
    "programming languages": "programming_languages",
    "habilidades blandas": "soft_skills",
    "habilidades interpersonales": "soft_skills",
    "soft skills": "soft_skills",
}

PROGRAMMING_LANGUAGES = {
    "bash",
    "c",
    "c#",
    "c++",
    "go",
    "java",
    "javascript",
    "kotlin",
    "php",
    "powershell",
    "python",
    "r",
    "ruby",
    "rust",
    "scala",
    "sql",
    "swift",
    "typescript",
}
TOOLS = {
    "ansible",
    "aws",
    "azure",
    "docker",
    "figma",
    "gcp",
    "git",
    "github",
    "gitlab",
    "jenkins",
    "jira",
    "kubernetes",
    "mysql",
    "oracle",
    "postgresql",
    "power bi",
    "redis",
    "tableau",
    "terraform",
}
SOFT_SKILLS = {
    "adaptabilidad",
    "adaptability",
    "comunicacion",
    "communication",
    "creatividad",
    "creativity",
    "leadership",
    "liderazgo",
    "problem solving",
    "resolucion de problemas",
    "teamwork",
    "trabajo en equipo",
}


@dataclass(frozen=True)
class SkillExtractionResult:
    """Habilidades clasificadas y advertencias de etiquetas desconocidas."""

    skills: dict[str, list[str]]
    warnings: list[str]


def extract_skills(lines: list[str]) -> dict[str, list[str]]:
    """
    Extrae habilidades manteniendo la interfaz publica original.

    Args:
        lines: Lineas de la seccion de habilidades.

    Returns:
        Diccionario compatible con el bloque `skills` del JSON.
    """
    return extract_skills_with_warnings(lines).skills


def extract_skills_with_warnings(
    lines: list[str],
) -> SkillExtractionResult:
    """
    Clasifica habilidades mediante etiquetas y vocabularios visibles.

    Args:
        lines: Lineas de la seccion de habilidades.

    Returns:
        Categorias ordenadas y advertencias de etiquetas ambiguas.
    """
    categorized: dict[str, list[str]] = {
        category: [] for category in SKILL_CATEGORIES
    }
    warnings: list[str] = []
    seen_values: set[str] = set()

    for line in clean_nonempty_lines(lines):
        cleaned_line = strip_bullet(line) if is_bullet_line(line) else line
        explicit_category, values = _split_labeled_skills(cleaned_line)

        if explicit_category is not None:
            for value in values:
                _append_skill(
                    categorized,
                    explicit_category,
                    value,
                    seen_values,
                )
            continue

        if ":" in cleaned_line:
            warnings.append(
                "skills contiene una etiqueta no reconocida; "
                "se aplico clasificacion por valor."
            )

        for value in values:
            category = _classify_skill(value)
            _append_skill(categorized, category, value, seen_values)

    return SkillExtractionResult(
        skills=categorized,
        warnings=deduplicate_preserving_order(warnings),
    )


def _split_labeled_skills(
    line: str,
) -> tuple[str | None, list[str]]:
    if ":" not in line:
        return None, split_values(line)

    label, raw_values = line.split(":", maxsplit=1)
    category = SKILL_LABELS.get(_normalize_label(label))
    return category, split_values(raw_values)


def _classify_skill(value: str) -> str:
    normalized_value = normalize_lookup_text(value)
    if normalized_value in PROGRAMMING_LANGUAGES:
        return "programming_languages"
    if normalized_value in TOOLS:
        return "tools"
    if normalized_value in SOFT_SKILLS:
        return "soft_skills"
    return "technical"


def _normalize_label(value: str) -> str:
    return normalize_lookup_text(value)


def _was_seen(value: str, seen_values: set[str]) -> bool:
    normalized_value = value.casefold()
    if normalized_value in seen_values:
        return True
    seen_values.add(normalized_value)
    return False


def _append_skill(
    categorized: dict[str, list[str]],
    category: str,
    value: str,
    seen_values: set[str],
) -> None:
    if not _was_seen(value, seen_values):
        categorized[category].append(value)
