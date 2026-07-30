"""
Modulo encargado de construir estructuras JSON serializables.

Une resultados parciales de los extractores en el contrato inicial del proyecto.
No realiza extraccion ni modifica el texto recibido.
"""

from cv_analyzer.contact_extractor import ContactInfo
from cv_analyzer.additional_sections_extractor import CertificationEntry
from cv_analyzer.additional_sections_extractor import CourseEntry, LanguageEntry
from cv_analyzer.additional_sections_extractor import ProjectEntry
from cv_analyzer.education_extractor import EducationEntry
from cv_analyzer.experience_extractor import ExperienceEntry


def build_basic_cv_result(
    *,
    full_name: str | None,
    professional_title: str | None,
    contact: ContactInfo,
    unclassified_text: list[str],
) -> dict[str, object]:
    """
    Construye una primera version serializable del resultado del curriculum.

    Args:
        full_name: Nombre detectado o None.
        professional_title: Titulo profesional detectado o None.
        contact: Datos de contacto extraidos.
        unclassified_text: Lineas que aun no se han clasificado.

    Returns:
        Diccionario compatible con JSON.
    """
    return {
        "personal_data": {
            "full_name": full_name,
            "professional_title": professional_title,
            "location": None,
            "summary": None,
        },
        "contact": contact.to_dict(),
        "education": [],
        "experience": [],
        "skills": {
            "technical": [],
            "tools": [],
            "programming_languages": [],
            "soft_skills": [],
        },
        "languages": [],
        "certifications": [],
        "courses": [],
        "projects": [],
        "metadata": {
            "source_file": None,
            "file_size_bytes": None,
            "page_count": None,
            "processed_at": None,
            "processed_successfully": True,
            "processing_version": "1.0",
            "warnings": [],
            "errors": [],
            "unclassified_text": list(unclassified_text),
        },
    }


def build_structured_cv_result(
    *,
    full_name: str | None,
    professional_title: str | None,
    contact: ContactInfo,
    education: list[EducationEntry],
    experience: list[ExperienceEntry],
    skills: dict[str, list[str]],
    languages: list[LanguageEntry],
    certifications: list[CertificationEntry],
    courses: list[CourseEntry],
    projects: list[ProjectEntry],
    unclassified_text: list[str],
    warnings: list[str] | None = None,
    summary: str | None = None,
    source_file: str | None = None,
    file_size_bytes: int | None = None,
    page_count: int | None = None,
    processed_at: str | None = None,
) -> dict[str, object]:
    """
    Construye el resultado JSON con secciones ya extraidas.

    Args:
        full_name: Nombre detectado o None.
        professional_title: Titulo profesional detectado o None.
        contact: Datos de contacto extraidos.
        education: Entradas de formacion.
        experience: Entradas de experiencia.
        skills: Habilidades clasificadas de forma inicial.
        languages: Idiomas detectados.
        certifications: Certificaciones detectadas.
        courses: Cursos detectados.
        projects: Proyectos detectados.
        unclassified_text: Lineas sin clasificar.
        warnings: Advertencias generadas durante el procesamiento.
        summary: Resumen o perfil profesional detectado.
        source_file: Nombre del archivo procesado.
        file_size_bytes: Tamano del archivo en bytes.
        page_count: Numero de paginas del documento.
        processed_at: Fecha y hora ISO 8601 del procesamiento.

    Returns:
        Diccionario compatible con JSON.
    """
    return {
        "personal_data": {
            "full_name": full_name,
            "professional_title": professional_title,
            "location": None,
            "summary": summary,
        },
        "contact": contact.to_dict(),
        "education": [entry.to_dict() for entry in education],
        "experience": [entry.to_dict() for entry in experience],
        "skills": {
            category: list(values)
            for category, values in skills.items()
        },
        "languages": [entry.to_dict() for entry in languages],
        "certifications": [entry.to_dict() for entry in certifications],
        "courses": [entry.to_dict() for entry in courses],
        "projects": [entry.to_dict() for entry in projects],
        "metadata": {
            "source_file": source_file,
            "file_size_bytes": file_size_bytes,
            "page_count": page_count,
            "processed_at": processed_at,
            "processed_successfully": True,
            "processing_version": "1.0",
            "warnings": list(warnings or []),
            "errors": [],
            "unclassified_text": list(unclassified_text),
        },
    }


def build_failed_cv_result(
    *,
    source_file: str | None,
    errors: list[str],
    processed_at: str,
    file_size_bytes: int | None = None,
    page_count: int | None = None,
    warnings: list[str] | None = None,
) -> dict[str, object]:
    """
    Construye una salida completa para un procesamiento fallido.

    Args:
        source_file: Nombre del archivo que se intento procesar.
        errors: Errores controlados que impidieron completar el analisis.
        processed_at: Fecha y hora ISO 8601 del intento.
        file_size_bytes: Tamano conocido del archivo, si esta disponible.
        page_count: Numero de paginas conocido, si esta disponible.
        warnings: Advertencias recopiladas antes del fallo.

    Returns:
        Diccionario con el mismo contrato JSON que un resultado correcto.
    """
    result = build_basic_cv_result(
        full_name=None,
        professional_title=None,
        contact=ContactInfo(),
        unclassified_text=[],
    )
    metadata = result["metadata"]

    if not isinstance(metadata, dict):
        raise TypeError("El constructor genero metadata invalida.")

    metadata.update(
        {
            "source_file": source_file,
            "file_size_bytes": file_size_bytes,
            "page_count": page_count,
            "processed_at": processed_at,
            "processed_successfully": False,
            "warnings": list(warnings or []),
            "errors": list(errors),
        }
    )
    return result
