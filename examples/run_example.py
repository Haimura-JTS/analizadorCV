"""Genera y procesa un CV sintetico sin conservar el PDF temporal."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory

import fitz

from cv_analyzer.pipeline import process_cv_file


EXAMPLES_DIRECTORY = Path(__file__).resolve().parent
SAMPLE_TEXT_PATH = EXAMPLES_DIRECTORY / "sample_cv.txt"
DEFAULT_OUTPUT_PATH = EXAMPLES_DIRECTORY / "output" / "sample_result.json"


def run_example(
    output_path: Path = DEFAULT_OUTPUT_PATH,
) -> dict[str, object]:
    """Procesa el ejemplo y escribe su resultado JSON."""
    sample_text = SAMPLE_TEXT_PATH.read_text(encoding="utf-8")

    with TemporaryDirectory(prefix="analizador-cv-example-") as directory:
        pdf_path = Path(directory) / "sample_cv.pdf"
        _create_text_pdf(pdf_path, sample_text)
        result = process_cv_file(pdf_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return result


def _create_text_pdf(file_path: Path, text: str) -> None:
    document = fitz.open()
    try:
        page = document.new_page()
        for line_number, line in enumerate(text.splitlines()):
            y_position = 72 + (line_number * 16)
            page.insert_text((72, y_position), line, fontsize=11)
        document.save(file_path)
    finally:
        document.close()


def main() -> None:
    """Ejecuta el ejemplo desde la linea de comandos."""
    result = run_example()
    metadata = result.get("metadata")
    succeeded = (
        isinstance(metadata, dict)
        and metadata.get("processed_successfully") is True
    )
    if not succeeded:
        raise SystemExit("El ejemplo no pudo procesarse correctamente.")

    print(f"Resultado guardado en: {DEFAULT_OUTPUT_PATH}")


if __name__ == "__main__":
    main()
