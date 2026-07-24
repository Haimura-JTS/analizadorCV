from pathlib import Path

from streamlit.testing.v1 import AppTest


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
    app.session_state["cv_analysis_result"] = _result()
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


def test_streamlit_app_keeps_running_for_failed_result() -> None:
    app = AppTest.from_file(PROJECT_ROOT / "app.py").run()
    app.session_state["cv_analysis_result"] = _result(successful=False)

    app.run()

    assert not app.exception
    assert app.error[0].value == "PDF no valido."
    assert app.download_button[0].label == "Descargar JSON"
