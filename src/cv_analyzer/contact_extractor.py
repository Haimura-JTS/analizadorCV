"""
Modulo encargado de extraer datos de contacto del curriculum.

Reconoce correo, telefono y enlaces habituales como LinkedIn, GitHub y
portfolio personal mediante expresiones regulares explicitas.

No valida identidad, no consulta servicios externos y no inventa datos ausentes.
"""

from collections.abc import Iterator
from dataclasses import asdict, dataclass
import re


# Reconoce direcciones de correo convencionales. No implementa una validacion
# completa de RFC 5322 porque el objetivo es extraccion practica desde CVs.
EMAIL_PATTERN = re.compile(
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
)

# Localiza candidatos de telefono con digitos y separadores convencionales.
# La funcion extract_phone aplica despues un limite de digitos para descartar
# rangos de anos y secuencias demasiado largas.
PHONE_PATTERN = re.compile(
    r"(?<![\w@])\+?\d(?:[\d(). \t-]*\d)?(?![\w@])"
)

# Reconoce URLs completas y dominios escritos sin protocolo. La limpieza
# posterior retira puntuacion propia de la frase, no de la URL.
URL_PATTERN = re.compile(
    r"(?:https?://)?(?:www\.)?[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?:/[^\s]*)?",
    re.IGNORECASE,
)
LINKEDIN_PROFILE_PATTERN = re.compile(
    r"(?:https?://\s*)?(?:www\.\s*)?"
    r"(?:[a-z]{2,3}\.)?linkedin\.com\s*/\s*"
    r"(?:in|pub|company)\s*/\s*[A-Za-z0-9._~%+-]+",
    re.IGNORECASE,
)

MIN_PHONE_DIGITS = 9
MAX_PHONE_DIGITS = 15
TRAILING_URL_PUNCTUATION = ".,;:!?)]}"


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
    for match in PHONE_PATTERN.finditer(text):
        candidate = " ".join(match.group(0).split())
        digit_count = sum(character.isdigit() for character in candidate)
        if MIN_PHONE_DIGITS <= digit_count <= MAX_PHONE_DIGITS:
            return candidate
    return None


def _normalize_url(url: str) -> str:
    """Anade protocolo a una URL cuando el curriculum no lo incluye."""
    cleaned_url = url.rstrip(TRAILING_URL_PUNCTUATION)
    if cleaned_url.lower().startswith(("http://", "https://")):
        return cleaned_url
    return f"https://{cleaned_url}"


def _find_url_containing(text: str, marker: str) -> str | None:
    for url in _iter_standalone_urls(text):
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
    profile_match = LINKEDIN_PROFILE_PATTERN.search(text)
    if profile_match is not None:
        compact_url = re.sub(r"\s+", "", profile_match.group(0))
        return _normalize_url(compact_url)
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
    for url in _iter_standalone_urls(text):
        lowered_url = url.lower()

        if "linkedin.com" not in lowered_url and "github.com" not in lowered_url:
            return _normalize_url(url)
    return None


def _iter_standalone_urls(text: str) -> Iterator[str]:
    email_spans = [match.span() for match in EMAIL_PATTERN.finditer(text)]

    for match in URL_PATTERN.finditer(text):
        overlaps_email = any(
            match.start() < email_end and match.end() > email_start
            for email_start, email_end in email_spans
        )
        if not overlaps_email:
            cleaned_url = match.group(0).rstrip(TRAILING_URL_PUNCTUATION)
            if cleaned_url:
                yield cleaned_url


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
