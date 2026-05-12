"""
Excepciones personalizadas jerárquicas para la aplicación.
Reemplaza las 11 instancias de `except Exception` genéricas.
"""

from typing import Optional, Any


class DocumentExtractionError(Exception):
    """Base exception para errores de extracción de documentos."""

    def __init__(
        self,
        message: str,
        details: Optional[dict] = None,
        original_error: Optional[Exception] = None
    ):
        """
        Inicializa la excepción.

        Args:
            message: Mensaje de error
            details: Detalles adicionales del error
            original_error: Excepción original si se está envolviendo
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.original_error = original_error

    def to_dict(self) -> dict:
        """Convierte la excepción a diccionario."""
        result = {
            "error_type": self.__class__.__name__,
            "message": self.message
        }
        if self.details:
            result["details"] = self.details
        return result


class AIServiceError(DocumentExtractionError):
    """Error en servicio de IA."""

    def __init__(
        self,
        message: str = "Error en servicio de IA",
        model: Optional[str] = None,
        **kwargs
    ):
        """
        Inicializa la excepción de IA.

        Args:
            message: Mensaje de error
            model: Modelo de IA que falló
            **kwargs: Argumentos adicionales
        """
        details = kwargs.pop("details", {})
        if model:
            details["model"] = model
        super().__init__(message, details=details, **kwargs)
        self.model = model


class AIServiceTimeoutError(AIServiceError):
    """Timeout en llamada a IA."""

    def __init__(
        self,
        message: str = "Timeout en llamada a IA",
        timeout_seconds: Optional[int] = None,
        **kwargs
    ):
        """
        Inicializa la excepción de timeout.

        Args:
            message: Mensaje de error
            timeout_seconds: Timeout en segundos
            **kwargs: Argumentos adicionales
        """
        details = kwargs.pop("details", {})
        if timeout_seconds:
            details["timeout_seconds"] = timeout_seconds
        super().__init__(message, details=details, **kwargs)
        self.timeout_seconds = timeout_seconds


class AIServiceRateLimitError(AIServiceError):
    """Excedido rate limit de IA."""

    def __init__(
        self,
        message: str = "Excedido rate limit de IA",
        retry_after: Optional[int] = None,
        **kwargs
    ):
        """
        Inicializa la excepción de rate limit.

        Args:
            message: Mensaje de error
            retry_after: Segundos antes de reintentar
            **kwargs: Argumentos adicionales
        """
        details = kwargs.pop("details", {})
        if retry_after:
            details["retry_after"] = retry_after
        super().__init__(message, details=details, **kwargs)
        self.retry_after = retry_after


class DocumentParsingError(DocumentExtractionError):
    """Error al parsear documento."""

    def __init__(
        self,
        message: str = "Error al parsear documento",
        file_type: Optional[str] = None,
        file_name: Optional[str] = None,
        **kwargs
    ):
        """
        Inicializa la excepción de parsing.

        Args:
            message: Mensaje de error
            file_type: Tipo de archivo
            file_name: Nombre del archivo
            **kwargs: Argumentos adicionales
        """
        details = kwargs.pop("details", {})
        if file_type:
            details["file_type"] = file_type
        if file_name:
            details["file_name"] = file_name
        super().__init__(message, details=details, **kwargs)
        self.file_type = file_type
        self.file_name = file_name


class PDFParsingError(DocumentParsingError):
    """Error específico al parsear PDF."""

    def __init__(
        self,
        message: str = "Error al parsear PDF",
        page_number: Optional[int] = None,
        **kwargs
    ):
        """
        Inicializa la excepción de PDF.

        Args:
            message: Mensaje de error
            page_number: Número de página que falló
            **kwargs: Argumentos adicionales
        """
        details = kwargs.pop("details", {})
        if page_number is not None:
            details["page_number"] = page_number
        kwargs["file_type"] = "PDF"
        super().__init__(message, details=details, **kwargs)
        self.page_number = page_number


class WordParsingError(DocumentParsingError):
    """Error específico al parsear Word."""

    def __init__(
        self,
        message: str = "Error al parsear Word",
        **kwargs
    ):
        """
        Inicializa la excepción de Word.

        Args:
            message: Mensaje de error
            **kwargs: Argumentos adicionales
        """
        kwargs["file_type"] = "Word"
        super().__init__(message, **kwargs)


class ValidationError(DocumentExtractionError):
    """Error de validación de datos extraídos."""

    def __init__(
        self,
        message: str = "Error de validación",
        field: Optional[str] = None,
        value: Optional[Any] = None,
        **kwargs
    ):
        """
        Inicializa la excepción de validación.

        Args:
            message: Mensaje de error
            field: Campo que falló la validación
            value: Valor que falló la validación
            **kwargs: Argumentos adicionales
        """
        details = kwargs.pop("details", {})
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = str(value)
        super().__init__(message, details=details, **kwargs)
        self.field = field
        self.value = value


class InconsistentDocumentError(ValidationError):
    """Error cuando las caras de un documento son inconsistentes."""

    def __init__(
        self,
        message: str = "Documento con datos inconsistentes",
        field: Optional[str] = None,
        frontal_value: Optional[Any] = None,
        back_value: Optional[Any] = None,
        **kwargs
    ):
        """
        Inicializa la excepción de inconsistencia.

        Args:
            message: Mensaje de error
            field: Campo inconsistente
            frontal_value: Valor de la cara frontal
            back_value: Valor de la cara trasera
            **kwargs: Argumentos adicionales
        """
        details = kwargs.pop("details", {})
        if field:
            details["field"] = field
        if frontal_value is not None:
            details["frontal_value"] = str(frontal_value)
        if back_value is not None:
            details["back_value"] = str(back_value)
        super().__init__(message, field=field, details=details, **kwargs)
        self.frontal_value = frontal_value
        self.back_value = back_value
