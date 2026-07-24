"""
Constantes compartidas por los modulos del analizador.

Incluye valores estables como extensiones permitidas y mensajes tecnicos
reutilizables. No contiene funciones de procesamiento.
"""

ALLOWED_PDF_EXTENSION = ".pdf"
PDF_EMPTY_TEXT_MESSAGE = "El PDF no contiene texto extraible."
PDF_PROTECTED_MESSAGE = (
    "El PDF esta protegido y no puede procesarse sin contrasena."
)
