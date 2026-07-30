"""Interfaz Streamlit del Analizador de CV."""

import logging
from typing import Protocol

import streamlit as st

from cv_analyzer.config import MAX_FILE_SIZE_BYTES
from cv_analyzer.pipeline import process_cv_file_with_details
from cv_analyzer.ui_helpers import build_download_name, format_file_size
from cv_analyzer.ui_helpers import serialize_cv_result
from cv_analyzer.ui_helpers import temporary_uploaded_pdf


logger = logging.getLogger(__name__)

RESULT_STATE_KEY = "cv_analysis_result"
TEXT_STATE_KEY = "cv_extracted_text"

APP_STYLES = """
<style>
    .stApp {
        background: #f7f9f8;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    .block-container {
        max-width: 1180px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3, h4, p, label, button {
        letter-spacing: 0 !important;
    }

    .app-kicker {
        color: #0f766e;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0 !important;
        margin-bottom: 0.25rem;
        text-transform: uppercase;
    }

    .app-subtitle {
        color: #52605c;
        font-size: 1rem;
        margin: 0.25rem 0 1.5rem;
    }

    [data-testid="stFileUploaderDropzone"] {
        background: #ffffff;
        border: 1px dashed #7e9992;
        border-radius: 6px;
    }

    [data-testid="stMetric"] {
        border-left: 2px solid #0f766e;
        padding-left: 0.9rem;
    }

    [data-testid="stAlert"],
    [data-testid="stExpander"],
    [data-testid="stStatusWidget"] {
        border-radius: 6px;
    }

    [data-testid="stButton"] button:focus-visible,
    [data-testid="stDownloadButton"] button:focus-visible {
        outline: 3px solid #d49a28;
        outline-offset: 2px;
    }

    [data-testid="stCaptionContainer"],
    [data-testid="stMarkdownContainer"] p {
        overflow-wrap: anywhere;
    }

    .privacy-note {
        border-left: 2px solid #d49a28;
        color: #52605c;
        font-size: 0.84rem;
        margin-top: 0.65rem;
        padding: 0.15rem 0 0.15rem 0.75rem;
    }

    @media (max-width: 640px) {
        .block-container {
            padding-top: 1.25rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }
    }
</style>
"""

EXPERIENCE_FIELDS = {
    "company": "Empresa",
    "position": "Puesto",
    "start_date": "Inicio",
    "end_date": "Fin",
    "current": "Actual",
    "description": "Descripción",
    "responsibilities": "Responsabilidades",
    "achievements": "Logros",
}
EDUCATION_FIELDS = {
    "institution": "Institución",
    "degree": "Titulación",
    "start_date": "Inicio",
    "end_date": "Fin",
    "status": "Estado",
    "description": "Descripción",
}
LANGUAGE_FIELDS = {
    "language": "Idioma",
    "level": "Nivel",
}
CERTIFICATION_FIELDS = {
    "name": "Certificación",
    "institution": "Institución",
    "date": "Fecha",
}
COURSE_FIELDS = {
    "name": "Curso",
    "institution": "Institución",
    "start_date": "Inicio",
    "end_date": "Fin",
    "status": "Estado",
}
PROJECT_FIELDS = {
    "name": "Proyecto",
    "description": "Descripción",
    "technologies": "Tecnologías",
    "url": "URL",
}
TABLE_VALUE_LABELS = {
    "in_progress": "En curso",
}


class UploadedPDF(Protocol):
    """Contrato mínimo del archivo recibido desde Streamlit."""

    name: str
    size: int

    def getvalue(self) -> bytes:
        """Devuelve el contenido binario cargado."""
        ...


def main() -> None:
    """Renderiza y coordina la interfaz web."""
    st.set_page_config(
        page_title="Analizador de CV",
        page_icon=":material/description:",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    st.markdown(APP_STYLES, unsafe_allow_html=True)
    _render_header()

    uploaded_file = st.file_uploader(
        "Currículum PDF",
        type=["pdf"],
        accept_multiple_files=False,
        key="cv_pdf_upload",
        help="Tamaño máximo: 10 MB.",
        on_change=_clear_analysis,
        max_upload_size=MAX_FILE_SIZE_BYTES // (1024 * 1024),
        width="stretch",
    )

    file_column, action_column = st.columns(
        [4, 1],
        gap="medium",
        vertical_alignment="center",
    )
    with file_column:
        if uploaded_file is not None:
            st.caption(
                f"{uploaded_file.name} · "
                f"{format_file_size(uploaded_file.size)}"
            )
    with action_column:
        analyze_requested = st.button(
            "Analizar",
            type="primary",
            icon=":material/search:",
            disabled=uploaded_file is None,
            width="stretch",
        )

    st.markdown(
        (
            '<div class="privacy-note">'
            "Privacidad: la copia temporal se elimina al finalizar y el "
            "analizador no envía el contenido a servicios externos."
            "</div>"
        ),
        unsafe_allow_html=True,
    )

    if analyze_requested and uploaded_file is not None:
        _process_upload(uploaded_file)

    stored_result = st.session_state.get(RESULT_STATE_KEY)
    stored_text = st.session_state.get(TEXT_STATE_KEY)
    if isinstance(stored_result, dict):
        _render_result(
            stored_result,
            stored_text if isinstance(stored_text, str) else None,
        )


def _render_header() -> None:
    st.markdown('<div class="app-kicker">Documentos</div>', unsafe_allow_html=True)
    st.title("Analizador de CV")
    st.markdown(
        '<p class="app-subtitle">Currículum PDF a JSON estructurado.</p>',
        unsafe_allow_html=True,
    )


def _clear_analysis() -> None:
    st.session_state.pop(RESULT_STATE_KEY, None)
    st.session_state.pop(TEXT_STATE_KEY, None)


def _process_upload(uploaded_file: UploadedPDF) -> None:
    _clear_analysis()
    status = st.status("Analizando documento", expanded=True)
    status.write("Validando el archivo y extrayendo el contenido.")

    try:
        with temporary_uploaded_pdf(
            uploaded_file.getvalue(),
            uploaded_file.name,
        ) as temporary_path:
            output = process_cv_file_with_details(temporary_path)
    except Exception:
        logger.exception("La interfaz no pudo preparar el archivo temporal.")
        status.update(
            label="No se pudo iniciar el análisis",
            state="error",
            expanded=True,
        )
        st.error(
            "No se pudo preparar el archivo para su procesamiento.",
            icon=":material/error:",
        )
        return

    st.session_state[RESULT_STATE_KEY] = output.data
    st.session_state[TEXT_STATE_KEY] = output.extracted_text

    if _processed_successfully(output.data):
        status.write("Estructura validada y lista para revisar.")
        status.update(
            label="Análisis completado",
            state="complete",
            expanded=False,
        )
    else:
        status.write("El documento produjo una salida controlada con errores.")
        status.update(
            label="Análisis finalizado con errores",
            state="error",
            expanded=True,
        )


def _render_result(
    result: dict[str, object],
    extracted_text: str | None,
) -> None:
    st.divider()
    metadata = _as_dict(result.get("metadata"))
    errors = _as_string_list(metadata.get("errors"))
    warnings = _as_string_list(metadata.get("warnings"))
    json_document = serialize_cv_result(result)

    heading_column, download_column = st.columns(
        [4, 1],
        gap="medium",
        vertical_alignment="center",
    )
    with heading_column:
        st.subheader("Resultado")
    with download_column:
        st.download_button(
            "Descargar JSON",
            data=json_document,
            file_name=build_download_name(metadata.get("source_file")),
            mime="application/json",
            type="primary",
            icon=":material/download:",
            on_click="ignore",
            width="stretch",
        )

    if _processed_successfully(result):
        st.success(
            "El currículum se procesó correctamente.",
            icon=":material/check_circle:",
        )
    elif not errors:
        st.error(
            "El análisis no pudo completarse.",
            icon=":material/error:",
        )

    if errors:
        st.error(
            _format_message_group("Se detectaron errores", errors),
            icon=":material/error:",
        )
    if warnings:
        st.warning(
            _format_message_group("Se detectaron advertencias", warnings),
            icon=":material/warning:",
        )

    _render_metrics(result, metadata, warnings)

    summary_tab, text_tab, json_tab = st.tabs(
        ["Resumen", "Texto extraído", "JSON"]
    )
    with summary_tab:
        _render_summary(result)
    with text_tab:
        _render_extracted_text(extracted_text)
    with json_tab:
        st.json(result, expanded=2)


def _render_metrics(
    result: dict[str, object],
    metadata: dict[str, object],
    warnings: list[str],
) -> None:
    page_count = _as_int(metadata.get("page_count"))
    section_items = sum(
        len(_as_dict_list(result.get(section_name)))
        for section_name in (
            "experience",
            "education",
            "languages",
            "certifications",
            "courses",
            "projects",
        )
    )
    skill_count = sum(
        len(_as_string_list(value))
        for value in _as_dict(result.get("skills")).values()
    )

    columns = st.columns(4, gap="medium")
    columns[0].metric(
        "Archivo",
        format_file_size(_as_int(metadata.get("file_size_bytes"))),
    )
    columns[1].metric(
        "Páginas",
        str(page_count) if page_count is not None and page_count >= 0 else "N/D",
    )
    columns[2].metric("Elementos", str(section_items + skill_count))
    columns[3].metric("Advertencias", str(len(warnings)))


def _render_summary(result: dict[str, object]) -> None:
    personal_data = _as_dict(result.get("personal_data"))
    contact = _as_dict(result.get("contact"))

    st.subheader(
        _display_value(personal_data.get("full_name"), "Nombre no detectado")
    )
    professional_title = personal_data.get("professional_title")
    if isinstance(professional_title, str) and professional_title:
        st.caption(professional_title)

    summary = personal_data.get("summary")
    if isinstance(summary, str) and summary:
        st.markdown("#### Perfil")
        st.write(summary)

    st.markdown("#### Contacto")
    contact_columns = st.columns(2, gap="large")
    contact_items = (
        ("Correo", contact.get("email")),
        ("Teléfono", contact.get("phone")),
        ("LinkedIn", contact.get("linkedin")),
        ("GitHub", contact.get("github")),
        ("Portfolio", contact.get("portfolio")),
    )
    for index, (label, value) in enumerate(contact_items):
        with contact_columns[index % 2]:
            st.caption(label)
            st.write(_display_value(value))

    _render_skills(_as_dict(result.get("skills")))
    _render_table_section(
        "Experiencia",
        _as_dict_list(result.get("experience")),
        EXPERIENCE_FIELDS,
    )
    _render_table_section(
        "Formación",
        _as_dict_list(result.get("education")),
        EDUCATION_FIELDS,
    )
    _render_table_section(
        "Idiomas",
        _as_dict_list(result.get("languages")),
        LANGUAGE_FIELDS,
    )
    _render_table_section(
        "Certificaciones",
        _as_dict_list(result.get("certifications")),
        CERTIFICATION_FIELDS,
    )
    _render_table_section(
        "Cursos",
        _as_dict_list(result.get("courses")),
        COURSE_FIELDS,
    )
    _render_table_section(
        "Proyectos",
        _as_dict_list(result.get("projects")),
        PROJECT_FIELDS,
    )


def _render_skills(skills: dict[str, object]) -> None:
    st.markdown("#### Habilidades")
    labels = {
        "technical": "Técnicas",
        "tools": "Herramientas",
        "programming_languages": "Lenguajes",
        "soft_skills": "Interpersonales",
    }
    columns = st.columns(2, gap="large")

    for index, (field_name, label) in enumerate(labels.items()):
        values = _as_string_list(skills.get(field_name))
        with columns[index % 2]:
            st.caption(label)
            st.write(", ".join(values) if values else "No detectadas")


def _render_table_section(
    title: str,
    entries: list[dict[str, object]],
    field_labels: dict[str, str],
) -> None:
    st.markdown(f"#### {title}")
    if not entries:
        st.caption("Sin registros detectados.")
        return

    rows = [
        {
            label: _format_table_value(entry.get(field_name))
            for field_name, label in field_labels.items()
        }
        for entry in entries
    ]
    st.dataframe(
        rows,
        hide_index=True,
        width="stretch",
    )


def _render_extracted_text(extracted_text: str | None) -> None:
    if not extracted_text:
        st.info(
            "No hay texto extraído disponible.",
            icon=":material/info:",
        )
        return

    st.text_area(
        "Texto extraído",
        value=extracted_text,
        height=520,
        disabled=True,
    )


def _processed_successfully(result: dict[str, object]) -> bool:
    metadata = _as_dict(result.get("metadata"))
    return metadata.get("processed_successfully") is True


def _as_dict(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        return {}
    return {
        key: item
        for key, item in value.items()
        if isinstance(key, str)
    }


def _as_dict_list(value: object) -> list[dict[str, object]]:
    if not isinstance(value, list):
        return []
    return [_as_dict(item) for item in value if isinstance(item, dict)]


def _as_string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    normalized_items: list[str] = []
    seen_items: set[str] = set()

    for item in value:
        if not isinstance(item, str):
            continue
        normalized_item = item.strip()
        if not normalized_item or normalized_item in seen_items:
            continue
        normalized_items.append(normalized_item)
        seen_items.add(normalized_item)

    return normalized_items


def _as_int(value: object) -> int | None:
    return value if type(value) is int else None


def _display_value(
    value: object,
    fallback: str = "No detectado",
) -> str:
    return value if isinstance(value, str) and value else fallback


def _format_table_value(value: object) -> str:
    if value is None or value == "":
        return ""
    if isinstance(value, bool):
        return "Sí" if value else "No"
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    string_value = str(value)
    return TABLE_VALUE_LABELS.get(string_value, string_value)


def _format_message_group(title: str, messages: list[str]) -> str:
    if len(messages) == 1:
        return messages[0]
    message_list = "\n".join(f"- {message}" for message in messages)
    return f"{title}:\n\n{message_list}"


if __name__ == "__main__":
    main()
