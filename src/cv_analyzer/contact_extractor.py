"""
Modulo encargado de extraer datos de contacto del curriculum.

Reconoce correo, telefono y enlaces habituales como LinkedIn, GitHub y
portfolio personal mediante expresiones regulares explicitas.

No valida identidad, no consulta servicios externos y no inventa datos ausentes.
"""

from dataclasses import asdict, dataclass
import re


# Reconoce direcciones de correo convencionales. No implementa una validacion
# completa de RFC 5322 porque el objetivo es extraccion practica desde CVs.
EMAIL_PATTERN = re.compile(
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
)

# Reconoce telefonos frecuentes en CVs europeos e internacionales. Puede
# capturar falsos positivos si una linea contiene muchos numeros separados.
PHONE_PATTERN = re.compile(
    r"(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?){2,5}\d{2,4}"
)

# Reconoce URLs completas y dominios escritos sin protocolo.
URL_PATTERN = re.compile(
    r"(?:https?://)?(?:www\.)?[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?:/[^\s]*)?"
)


@dataclass(frozen=True)
class ContactInfo:
    """
    Datos de contacto extraidos del curriculum.

    Los campos ausentes se representan como None para no inventar informacion.
    """

    email: str | None = None
    phone: str | None = None
    linkedin: str | None = None
    github: str | None = None
    portfolio: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        """Convierte el resultado en un diccionario serializable."""
        return asdict(self)


def extract_email(text: str) -> str | None:
    """
    Extrae la primera direccion de correo encontrada.

    Args:
        text: Texto limpio del curriculum.

    Returns:
        Correo detectado o None si no hay coincidencias.
    """
    match = EMAIL_PATTERN.search(text)
    return match.group(0) if match else None


def extract_phone(text: str) -> str | None:
    """
    Extrae el primer telefono probable encontrado.

    Args:
        text: Texto limpio del curriculum.

    Returns:
        Telefono detectado o None si no hay coincidencias fiables.
    """
    match = PHONE_PATTERN.search(text)
    return match.group(0).strip() if match else None


def _normalize_url(url: str) -> str:
    """Anade protocolo a una URL cuando el curriculum no lo incluye."""
    if url.startswith(("http://", "https://")):
        return url
    return f"https://{url}"


def _find_url_containing(text: str, marker: str) -> str | None:
    for match in URL_PATTERN.finditer(text):
        url = match.group(0)
        if marker in url.lower():
            return _normalize_url(url)
    return None


def extract_linkedin(text: str) -> str | None:
    """
    Extrae una URL de LinkedIn si aparece en el texto.

    Args:
        text: Texto limpio del curriculum.

    Returns:
        URL normalizada o None.
    """
    return _find_url_containing(text, "linkedin.com")


def extract_github(text: str) -> str | None:
    """
    Extrae una URL de GitHub si aparece en el texto.

    Args:
        text: Texto limpio del curriculum.

    Returns:
        URL normalizada o None.
    """
    return _find_url_containing(text, "github.com")


def extract_portfolio(text: str) -> str | None:
    """
    Extrae una posible URL de portfolio distinta de LinkedIn y GitHub.

    Args:
        text: Texto limpio del curriculum.

    Returns:
        URL normalizada o None.
    """
    for match in URL_PATTERN.finditer(text):
        url = match.group(0)
        lowered_url = url.lower()
        previous_character = text[match.start() - 1] if match.start() > 0 else ""

        if "linkedin.com" not in lowered_url and "github.com" not in lowered_url:
            if previous_character == "@":
                continue
            return _normalize_url(url)
    return None


def extract_contact_info(text: str) -> ContactInfo:
    """
    Extrae los datos de contacto principales del curriculum.

    Args:
        text: Texto limpio del curriculum.

    Returns:
        Objeto ContactInfo con campos detectados o None.
    """
    return ContactInfo(
        email=extract_email(text),
        phone=extract_phone(text),
        linkedin=extract_linkedin(text),
        github=extract_github(text),
        portfolio=extract_portfolio(text),
    )
