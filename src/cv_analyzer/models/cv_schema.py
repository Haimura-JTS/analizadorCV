"""
Modelos Pydantic que representan el esquema JSON del curriculum.

Definen tipos, valores por defecto y estructura de salida. No contienen
logica de extraccion ni heuristicas de interpretacion.
"""

from pydantic import BaseModel, ConfigDict, Field


class StrictCVModel(BaseModel):
    """Base comun para impedir campos inesperados en el resultado."""

    model_config = ConfigDict(extra="forbid")


class PersonalDataModel(StrictCVModel):
    """Datos personales basicos del curriculum."""

    full_name: str | None = None
    professional_title: str | None = None
    location: str | None = None
    summary: str | None = None


class ContactModel(StrictCVModel):
    """Datos de contacto extraidos del curriculum."""

    email: str | None = None
    phone: str | None = None
    linkedin: str | None = None
    github: str | None = None
    portfolio: str | None = None


class EducationModel(StrictCVModel):
    """Entrada de formacion academica."""

    institution: str | None = None
    degree: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    status: str | None = None
    description: str | None = None


class ExperienceModel(StrictCVModel):
    """Entrada de experiencia profesional."""

    company: str | None = None
    position: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    current: bool = False
    description: str | None = None
    responsibilities: list[str] = Field(default_factory=list)
    achievements: list[str] = Field(default_factory=list)


class SkillsModel(StrictCVModel):
    """Habilidades agrupadas por categorias iniciales."""

    technical: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)
    programming_languages: list[str] = Field(default_factory=list)
    soft_skills: list[str] = Field(default_factory=list)


class LanguageModel(StrictCVModel):
    """Idioma y nivel detectados."""

    language: str | None = None
    level: str | None = None


class CertificationModel(StrictCVModel):
    """Certificacion detectada."""

    name: str | None = None
    institution: str | None = None
    date: str | None = None


class CourseModel(StrictCVModel):
    """Curso detectado."""

    name: str | None = None
    institution: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    status: str | None = None


class ProjectModel(StrictCVModel):
    """Proyecto detectado."""

    name: str | None = None
    description: str | None = None
    technologies: list[str] = Field(default_factory=list)
    url: str | None = None


class MetadataModel(StrictCVModel):
    """Metadatos tecnicos del procesamiento."""

    source_file: str | None = None
    file_size_bytes: int | None = None
    page_count: int | None = None
    processed_at: str | None = None
    processed_successfully: bool = False
    processing_version: str = "1.0"
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    unclassified_text: list[str] = Field(default_factory=list)


class CVResultModel(StrictCVModel):
    """Resultado completo del Analizador de CV."""

    personal_data: PersonalDataModel = Field(default_factory=PersonalDataModel)
    contact: ContactModel = Field(default_factory=ContactModel)
    education: list[EducationModel] = Field(default_factory=list)
    experience: list[ExperienceModel] = Field(default_factory=list)
    skills: SkillsModel = Field(default_factory=SkillsModel)
    languages: list[LanguageModel] = Field(default_factory=list)
    certifications: list[CertificationModel] = Field(default_factory=list)
    courses: list[CourseModel] = Field(default_factory=list)
    projects: list[ProjectModel] = Field(default_factory=list)
    metadata: MetadataModel = Field(default_factory=MetadataModel)

