"""
Extractor y clasificador conservador de habilidades.

Respeta etiquetas explicitas y utiliza listas visibles para distinguir
lenguajes, herramientas y habilidades interpersonales. Los valores no
reconocidos se conservan como habilidades tecnicas.

No calcula niveles de dominio ni infiere habilidades ausentes.
"""

from dataclasses import dataclass
import re

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

AUTO_CLASSIFICATION_LABEL = "auto"

SKILL_LABELS = {
    "aptitudes tecnicas": "technical",
    "bases de datos": AUTO_CLASSIFICATION_LABEL,
    "competencias": AUTO_CLASSIFICATION_LABEL,
    "competencias clave": AUTO_CLASSIFICATION_LABEL,
    "competencias profesionales": AUTO_CLASSIFICATION_LABEL,
    "conocimientos": AUTO_CLASSIFICATION_LABEL,
    "databases": AUTO_CLASSIFICATION_LABEL,
    "frameworks": "technical",
    "frameworks y librerias": "technical",
    "hard skills": "technical",
    "librerias": "technical",
    "metodologias": "technical",
    "skills": AUTO_CLASSIFICATION_LABEL,
    "stack tecnologico": AUTO_CLASSIFICATION_LABEL,
    "tech stack": AUTO_CLASSIFICATION_LABEL,
    "technical": "technical",
    "technical skills": "technical",
    "tecnologias": AUTO_CLASSIFICATION_LABEL,
    "tecnologias y herramientas": AUTO_CLASSIFICATION_LABEL,
    "herramientas": "tools",
    "herramientas y tecnologias": AUTO_CLASSIFICATION_LABEL,
    "platforms": "tools",
    "plataformas": "tools",
    "software": "tools",
    "tools": "tools",
    "lenguajes": "programming_languages",
    "lenguajes de programacion": "programming_languages",
    "programming languages": "programming_languages",
    "habilidades blandas": "soft_skills",
    "habilidades interpersonales": "soft_skills",
    "competencias interpersonales": "soft_skills",
    "people skills": "soft_skills",
    "soft skills": "soft_skills",
}

SKILL_VALUE_SEPARATOR_PATTERN = re.compile(r"[,;|]|\s+/\s+")
SKILL_LEVEL_SUFFIX_PATTERN = re.compile(
    r"\s*(?:\((?:nivel\s+)?(?:basico|basic|intermedio|intermediate|"
    r"avanzado|advanced|experto|expert)\)|"
    r"(?:-|:)\s*(?:basico|basic|intermedio|intermediate|"
    r"avanzado|advanced|experto|expert))$",
    re.IGNORECASE,
)

PROGRAMMING_LANGUAGES = {
    "bash",
    "c",
    "c#",
    "c++",
    "go",
    "groovy",
    "java",
    "javascript",
    "kotlin",
    "matlab",
    "objective-c",
    "perl",
    "php",
    "pl/sql",
    "powershell",
    "python",
    "r",
    "ruby",
    "rust",
    "scala",
    "sql",
    "swift",
    "transact-sql",
    "typescript",
    "vba",
}
TOOLS = {
    "adobe illustrator",
    "adobe photoshop",
    "android studio",
    "ansible",
    "aws",
    "azure",
    "azure devops",
    "bitbucket",
    "confluence",
    "databricks",
    "dbeaver",
    "docker",
    "eclipse",
    "excel",
    "figma",
    "gcp",
    "git",
    "github",
    "gitlab",
    "jenkins",
    "jira",
    "jupyter",
    "kubernetes",
    "linux",
    "microsoft 365",
    "mongodb",
    "mysql",
    "notion",
    "oracle",
    "postgresql",
    "power bi",
    "powerbi",
    "pycharm",
    "red hat",
    "redis",
    "salesforce",
    "sap",
    "snowflake",
    "splunk",
    "sql server",
    "sqlite",
    "swagger",
    "tableau",
    "talend",
    "teams",
    "terraform",
    "trello",
    "visual studio",
    "visual studio code",
    "vscode",
    "windows",
    "wordpress",
}
SOFT_SKILLS = {
    "adaptabilidad",
    "adaptability",
    "analytical thinking",
    "atencion al detalle",
    "autonomia",
    "autonomy",
    "capacidad analitica",
    "collaboration",
    "colaboracion",
    "comunicacion",
    "comunicacion efectiva",
    "comunicacion oral y escrita",
    "communication",
    "conflict resolution",
    "creatividad",
    "creativity",
    "critical thinking",
    "empatia",
    "empathy",
    "escucha activa",
    "flexibilidad",
    "flexibility",
    "gestion de conflictos",
    "gestion del tiempo",
    "iniciativa",
    "initiative",
    "inteligencia emocional",
    "leadership",
    "liderazgo",
    "negociacion",
    "negotiation",
    "organizacion",
    "organization",
    "pensamiento analitico",
    "pensamiento critico",
    "proactividad",
    "proactivity",
    "problem solving",
    "resilience",
    "resiliencia",
    "resolucion de problemas",
    "teamwork",
    "time management",
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

        if (
            explicit_category is not None
            and explicit_category != AUTO_CLASSIFICATION_LABEL
        ):
            for value in values:
                _append_skill(
                    categorized,
                    explicit_category,
                    value,
                    seen_values,
                )
            continue

        if ":" in cleaned_line and explicit_category is None:
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
        return None, _split_skill_values(line)

    label, raw_values = line.split(":", maxsplit=1)
    category = SKILL_LABELS.get(_normalize_label(label))
    return category, _split_skill_values(raw_values)


def _classify_skill(value: str) -> str:
    normalized_value = _normalized_skill_key(value)
    if normalized_value in PROGRAMMING_LANGUAGES:
        return "programming_languages"
    if normalized_value in TOOLS:
        return "tools"
    if normalized_value in SOFT_SKILLS:
        return "soft_skills"
    return "technical"


def _normalize_label(value: str) -> str:
    return normalize_lookup_text(value)


def _normalized_skill_key(value: str) -> str:
    normalized_value = normalize_lookup_text(value)
    return SKILL_LEVEL_SUFFIX_PATTERN.sub("", normalized_value).strip()


def _split_skill_values(value: str) -> list[str]:
    return [
        item.strip()
        for item in SKILL_VALUE_SEPARATOR_PATTERN.split(value)
        if item.strip()
    ]


def _was_seen(value: str, seen_values: set[str]) -> bool:
    normalized_value = normalize_lookup_text(value)
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
