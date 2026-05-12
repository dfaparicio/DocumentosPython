"""
Funciones de seguridad y validación de archivos.
Sanitiza entradas y valida tipos de archivos con python-magic.
"""

import logging
import mimetypes
from typing import Optional, Tuple
from pathlib import Path

# Intentar importar python-magic, si no está disponible usar mimetypes
try:
    import magic
    HAS_MAGIC = True
except ImportError:
    HAS_MAGIC = False
    magic = None

from config import get_settings

logger = logging.getLogger(__name__)

# Configuración de validación de archivos
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB en bytes
MAX_PDF_PAGES = 100
ALLOWED_MIME_TYPES = [
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
]
ALLOWED_EXTENSIONS = {".pdf", ".docx"}


def validate_file_size(file_size: int) -> bool:
    """
    Valida que el tamaño del archivo sea aceptable.

    Args:
        file_size: Tamaño del archivo en bytes

    Returns:
        True si el tamaño es válido

    Raises:
        ValueError: Si el tamaño excede el máximo permitido
    """
    settings = get_settings()
    max_size = settings.max_file_size_mb * 1024 * 1024

    if file_size > max_size:
        logger.warning(
            f"Archivo excede tamaño máximo permitido",
            extra={
                "file_size_mb": file_size / (1024 * 1024),
                "max_size_mb": settings.max_file_size_mb
            }
        )
        raise ValueError(
            f"Archivo demasiado grande: {file_size / (1024 * 1024):.2f}MB. "
            f"Máximo permitido: {settings.max_file_size_mb}MB"
        )
    return True


def validate_file_extension(filename: str) -> bool:
    """
    Valida que la extensión del archivo sea permitida.

    Args:
        filename: Nombre del archivo

    Returns:
        True si la extensión es válida

    Raises:
        ValueError: Si la extensión no es permitida
    """
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        logger.warning(f"Extensión de archivo no permitida: {ext}")
        raise ValueError(
            f"Extensión de archivo no permitida: {ext}. "
            f"Extensiones permitidas: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    return True


def detect_file_type(file_bytes: bytes, filename: Optional[str] = None) -> Tuple[str, str]:
    """
    Detecta el tipo de archivo usando python-magic o mimetypes.

    Args:
        file_bytes: Contenido del archivo en bytes
        filename: Nombre del archivo (opcional, para fallback)

    Returns:
        Tupla (mime_type, type_description)

    Raises:
        ValueError: Si no se puede detectar el tipo de archivo
    """
    settings = get_settings()

    # Intentar usar python-magic para detección más precisa
    if HAS_MAGIC:
        try:
            mime = magic.Magic(mime=True)
            mime_type = mime.from_buffer(file_bytes)
            logger.debug(f"Tipo MIME detectado: {mime_type}")
        except Exception as e:
            logger.warning(f"Error al detectar tipo MIME con python-magic: {e}")
            mime_type = None
    else:
        mime_type = None

    # Fallback a mimetypes si python-magic falla o no está disponible
    if mime_type is None and filename:
        mime_type, _ = mimetypes.guess_type(filename)
        logger.debug(f"Tipo MIME inferido desde extensión: {mime_type}")

    # Validar que el tipo detectado sea permitido
    if mime_type not in ALLOWED_MIME_TYPES:
        logger.warning(
            f"Tipo de archivo no permitido",
            extra={"detected_type": mime_type, "filename": filename}
        )
        raise ValueError(
            f"Tipo de archivo no permitido: {mime_type}. "
            f"Tipos permitidos: {', '.join(ALLOWED_MIME_TYPES)}"
        )

    # Descripción del tipo
    type_description = "PDF" if mime_type == "application/pdf" else "Word"

    return mime_type, type_description


def sanitize_input(text: str, max_length: Optional[int] = None) -> str:
    """
    Sanitiza texto de entrada para evitar inyección.

    Args:
        text: Texto a sanitizar
        max_length: Longitud máxima permitida (opcional)

    Returns:
        Texto sanitizado
    """
    if not text:
        return ""

    # Eliminar caracteres peligrosos
    text = text.strip()

    # Limitar longitud si se especifica
    if max_length and len(text) > max_length:
        logger.warning(f"Texto truncado por exceder longitud máxima", extra={"max_length": max_length})
        text = text[:max_length]

    return text


def validate_pdf_page_count(page_count: int) -> bool:
    """
    Valida que el número de páginas sea aceptable.

    Args:
        page_count: Número de páginas

    Returns:
        True si el número de páginas es válido

    Raises:
        ValueError: Si el número de páginas excede el máximo
    """
    settings = get_settings()

    if page_count > settings.max_pdf_pages:
        logger.warning(
            f"PDF excede número máximo de páginas",
            extra={"page_count": page_count, "max_pages": settings.max_pdf_pages}
        )
        raise ValueError(
            f"PDF tiene demasiadas páginas: {page_count}. "
            f"Máximo permitido: {settings.max_pdf_pages}"
        )
    return True


def validate_and_sanitize_upload(file_bytes: bytes, filename: str) -> dict:
    """
    Valida y sanitiza un archivo subido.

    Args:
        file_bytes: Contenido del archivo
        filename: Nombre del archivo

    Returns:
        Diccionario con información de validación

    Raises:
        ValueError: Si alguna validación falla
    """
    file_size = len(file_bytes)

    # Validar tamaño
    validate_file_size(file_size)

    # Validar extensión
    validate_file_extension(filename)

    # Detectar tipo de archivo
    mime_type, type_description = detect_file_type(file_bytes, filename)

    logger.info(
        f"Archivo validado exitosamente",
        extra={
            "filename": filename,
            "size_mb": file_size / (1024 * 1024),
            "mime_type": mime_type,
            "type": type_description
        }
    )

    return {
        "filename": sanitize_input(filename),
        "size_bytes": file_size,
        "mime_type": mime_type,
        "type": type_description,
        "is_valid": True
    }
