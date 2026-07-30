"""
Excepciones propias del dominio del Analizador de CV.

Permiten diferenciar errores esperados durante la lectura de archivos de
fallos inesperados del programa.
"""


class CVAnalyzerError(Exception):
    """Error base del proyecto."""


class InvalidFileTypeError(CVAnalyzerError):
    """Se lanza cuando el archivo recibido no tiene extension PDF."""


class FileTooLargeError(CVAnalyzerError):
    """Se lanza cuando el archivo supera el tamano maximo permitido."""


class EmptyDocumentError(CVAnalyzerError):
    """Se lanza cuando el documento no contiene texto extraible."""


class ScannedPDFError(EmptyDocumentError):
    """Se lanza cuando un PDF parece contener solo imagenes sin texto."""


class ProtectedPDFError(CVAnalyzerError):
    """Base compatible para errores de PDF protegido."""


class PasswordProtectedPDFError(ProtectedPDFError):
    """Se lanza cuando el PDF requiere contraseña."""


class PDFReadError(CVAnalyzerError):
    """Se lanza cuando el PDF no puede abrirse o leerse correctamente."""
