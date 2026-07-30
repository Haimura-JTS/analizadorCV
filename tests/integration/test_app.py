from pathlib import Path

from streamlit.testing.v1 import AppTest

from app import _format_message_group, _format_table_value


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _result(*, successful: bool = True) -> dict[str, object]:
    return {
        "personal_data": {
            "full_name": "Ana Garcia",
            "professional_title": "Backend Developer",
            "location": None,
            "summary": "Desarrolladora de servicios web.",
        },
        "contact": {},
        "education": [],
        "experience": [],
        "skills": {},
        "languages": [],
        "certifications": [],
        "courses": [],
        "projects": [],
        "metadata": {
            "source_file": "ana.pdf",
            "file_size_bytes": 1024,
            "page_count": 1,
            "processed_successfully": successful,
            "warnings": [],
            "errors": [] if successful else ["PDF no valido."],
        },
    }


def test_streamlit_app_starts_with_upload_workflow() -> None:
    app = AppTest.from_file(PROJECT_ROOT / "app.py").run()

    assert not app.exception
    assert app.title[0].value == "Analizador de CV"
    assert len(app.file_uploader) == 1
    assert app.file_uploader[0].label == "Currículum PDF"
    assert app.button[0].label == "Analizar"
    assert app.button[0].disabled is True
    assert any(
        "Privacidad:" in markdown.value
        for markdown in app.markdown
    )


def test_streamlit_app_renders_result_views_and_download() -> None:
    app = AppTest.from_file(PROJECT_ROOT / "app.py").run()
    result = _result()
    result["skills"] = {"technical": ["Python"]}
    result["experience"] = [
        {
            "company": "Acme",
            "position": "Backend Developer",
        }
    ]
    app.session_state["cv_analysis_result"] = result
    app.session_state["cv_extracted_text"] = "Ana Garcia\nBackend Developer"

    app.run()

    assert not app.exception
    assert [tab.label for tab in app.tabs] == [
        "Resumen",
        "Texto extraído",
        "JSON",
    ]
    assert app.text_area[0].value == "Ana Garcia\nBackend Developer"
    assert len(app.json) == 1
    assert app.download_button[0].label == "Descargar JSON"
    assert [(metric.label, metric.value) for metric in app.metric] == [
        ("Archivo", "1.0 KB"),
        ("Páginas", "1"),
        ("Elementos", "2"),
        ("Advertencias", "0"),
    ]


def test_streamlit_app_keeps_running_for_failed_result() -> None:
    app = AppTest.from_file(PROJECT_ROOT / "app.py").run()
    app.session_state["cv_analysis_result"] = _result(successful=False)

    app.run()

    assert not app.exception
    assert app.error[0].value == "PDF no valido."
    assert app.download_button[0].label == "Descargar JSON"
    assert app.info[0].value == "No hay texto extraído disponible."


def test_streamlit_app_groups_and_deduplicates_warnings() -> None:
    app = AppTest.from_file(PROJECT_ROOT / "app.py").run()
    result = _result()
    metadata = result["metadata"]
    assert isinstance(metadata, dict)
    metadata["warnings"] = [
        "Página sin texto.",
        " ",
        "Página sin texto.",
        "Sección ambigua.",
    ]
    metadata["file_size_bytes"] = True
    metadata["page_count"] = True
    app.session_state["cv_analysis_result"] = result

    app.run()

    assert not app.exception
    assert len(app.warning) == 1
    assert app.warning[0].value == (
        "Se detectaron advertencias:\n\n"
        "- Página sin texto.\n"
        "- Sección ambigua."
    )
    assert [(metric.label, metric.value) for metric in app.metric] == [
        ("Archivo", "No disponible"),
        ("Páginas", "N/D"),
        ("Elementos", "0"),
        ("Advertencias", "2"),
    ]


def test_presentation_helpers_translate_internal_values_and_group_messages() -> None:
    assert _format_table_value("in_progress") == "En curso"
    assert _format_table_value(True) == "Sí"
    assert _format_message_group("Errores", ["Error único."]) == "Error único."
