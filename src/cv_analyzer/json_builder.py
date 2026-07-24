"""
Modulo encargado de construir estructuras JSON serializables.

Une resultados parciales de los extractores en el contrato inicial del proyecto.
No realiza extraccion ni modifica el texto recibido.
"""

from cv_analyzer.contact_extractor import ContactInfo


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
            "unclassified_text": unclassified_text,
        },
    }

