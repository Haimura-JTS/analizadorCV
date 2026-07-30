"""
Constantes compartidas por los modulos del analizador.

Incluye valores estables como extensiones permitidas y mensajes tecnicos
reutilizables. No contiene funciones de procesamiento.
"""

ALLOWED_PDF_EXTENSION = ".pdf"
FILE_NOT_FOUND_MESSAGE = "No existe el archivo indicado."
FILE_IS_DIRECTORY_MESSAGE = (
    "La ruta indicada no corresponde a un archivo."
)
FILE_ACCESS_ERROR_MESSAGE = "No se pudo acceder al archivo PDF."
PDF_EMPTY_FILE_MESSAGE = "El archivo PDF esta vacio."
PDF_EMPTY_TEXT_MESSAGE = "El PDF no contiene texto extraible."
PDF_NO_PAGES_MESSAGE = "El PDF no contiene paginas."
PDF_PROTECTED_MESSAGE = (
    "El PDF esta protegido y no puede procesarse sin contrasena."
)
PDF_SCANNED_MESSAGE = (
    "El PDF parece estar escaneado y no contiene texto extraible."
)
PDF_SCANNED_PAGES_WARNING_TEMPLATE = (
    "Paginas posiblemente escaneadas sin texto extraible: {pages}."
)
PDF_EMPTY_PAGES_WARNING_TEMPLATE = (
    "Paginas vacias o sin texto extraible: {pages}."
)
INVALID_RESULT_MESSAGE = (
    "El resultado generado no cumple el contrato JSON esperado."
)
EXPECTED_PROCESSING_ERROR_MESSAGE = (
    "No se pudo procesar el documento PDF."
)
UNEXPECTED_PROCESSING_ERROR_MESSAGE = (
    "Ocurrio un error interno durante el procesamiento del CV."
)
