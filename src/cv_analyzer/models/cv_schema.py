"""
Modelos Pydantic que representan el esquema JSON del curriculum.

Definen tipos, valores por defecto y estructura de salida. No contienen
logica de extraccion ni heuristicas de interpretacion.
"""

from datetime import datetime, timedelta
from typing import Annotated, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
    model_validator,
)


# Estos patrones validan el formato de salida, no extraen valores del PDF.
PartialDate = Annotated[
    str,
    StringConstraints(pattern=r"^\d{4}(?:-(?:0[1-9]|1[0-2]))?$"),
]
EmailValue = Annotated[
    str,
    StringConstraints(
        pattern=r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$"
    ),
]
HttpUrlValue = Annotated[
    str,
    StringConstraints(pattern=r"^[Hh][Tt][Tt][Pp][Ss]?://\S+$"),
]


class StrictCVModel(BaseModel):
    """Base comun para impedir campos inesperados en el resultado."""

    model_config = ConfigDict(extra="forbid", strict=True)


class PersonalDataModel(StrictCVModel):
    """Datos personales basicos del curriculum."""

    full_name: str | None = None
    professional_title: str | None = None
    location: str | None = None
    summary: str | None = None


class ContactModel(StrictCVModel):
    """Datos de contacto extraidos del curriculum."""

    email: EmailValue | None = None
    phone: str | None = None
    linkedin: HttpUrlValue | None = None
    github: HttpUrlValue | None = None
    portfolio: HttpUrlValue | None = None


class EducationModel(StrictCVModel):
    """Entrada de formacion academica."""

    institution: str | None = None
    degree: str | None = None
    start_date: PartialDate | None = Field(
        default=None,
        description="Fecha parcial normalizada como YYYY o YYYY-MM.",
    )
    end_date: PartialDate | None = Field(
        default=None,
        description="Fecha parcial normalizada como YYYY o YYYY-MM.",
    )
    status: str | None = Field(
        default=None,
        description="Estado explicito; `in_progress` indica actualidad.",
    )
    description: str | None = None


class ExperienceModel(StrictCVModel):
    """Entrada de experiencia profesional."""

    company: str | None = None
    position: str | None = None
    start_date: PartialDate | None = Field(
        default=None,
        description="Fecha parcial normalizada como YYYY o YYYY-MM.",
    )
    end_date: PartialDate | None = Field(
        default=None,
        description="Fecha parcial normalizada como YYYY o YYYY-MM.",
    )
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
    date: PartialDate | None = Field(
        default=None,
        description="Fecha parcial normalizada como YYYY o YYYY-MM.",
    )


class CourseModel(StrictCVModel):
    """Curso detectado."""

    name: str | None = None
    institution: str | None = None
    start_date: PartialDate | None = Field(
        default=None,
        description="Fecha parcial normalizada como YYYY o YYYY-MM.",
    )
    end_date: PartialDate | None = Field(
        default=None,
        description="Fecha parcial normalizada como YYYY o YYYY-MM.",
    )
    status: str | None = Field(
        default=None,
        description="Estado explicito; `in_progress` indica actualidad.",
    )


class ProjectModel(StrictCVModel):
    """Proyecto detectado."""

    name: str | None = None
    description: str | None = None
    technologies: list[str] = Field(default_factory=list)
    url: str | None = None


class MetadataModel(StrictCVModel):
    """Metadatos tecnicos del procesamiento."""

    source_file: str | None = None
    file_size_bytes: int | None = Field(default=None, ge=0)
    page_count: int | None = Field(default=None, ge=0)
    processed_at: str | None = Field(
        default=None,
        description="Marca temporal ISO 8601 con zona UTC.",
    )
    processed_successfully: bool = False
    processing_version: str = "1.0"
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    unclassified_text: list[str] = Field(default_factory=list)

    @field_validator("processed_at")
    @classmethod
    def validate_processed_at(cls, value: str | None) -> str | None:
        """Comprueba ISO 8601 y exige una zona equivalente a UTC."""
        if value is None:
            return None
        try:
            parsed_value = datetime.fromisoformat(value)
        except ValueError as error:
            raise ValueError(
                "processed_at debe usar formato ISO 8601."
            ) from error
        if parsed_value.utcoffset() != timedelta(0):
            raise ValueError("processed_at debe incluir una zona UTC.")
        return value

    @model_validator(mode="after")
    def validate_processing_state(self) -> Self:
        """Impide declarar exito cuando existen errores registrados."""
        if self.processed_successfully and self.errors:
            raise ValueError(
                "processed_successfully no puede ser true si existen errores."
            )
        return self


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
