"""
Excepciones personalizadas jerárquicas para la aplicación.
Reemplaza las 11 instancias de `except Exception` genéricas.

Hierarchical custom exceptions for the application.
Replaces the 11 instances of generic `except Exception`.
"""

from typing import Optional, Any


class DocumentExtractionError(Exception):
    """Base exception para errores de extracción de documentos.
    Base exception for document extraction errors."""

    def __init__(
        self,
        message: str,
        details: Optional[dict] = None,
        original_error: Optional[Exception] = None
    ):
        """
        Inicializa la excepción.
        Initializes the exception.

        Args:
            message: Mensaje de error / Error message
            details: Detalles adicionales del error / Additional error details
            original_error: Excepción original si se está envolviendo / Original exception if wrapping
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.original_error = original_error

    def to_dict(self) -> dict:
        """Convierte la excepción a diccionario.
        Converts the exception to a dictionary."""
        result = {
            "error_type": self.__class__.__name__,
            "message": self.message
        }
        if self.details:
            result["details"] = self.details
        return result


class AIServiceError(DocumentExtractionError):
    """Error en servicio de IA.
    Error in AI service."""

    def __init__(
        self,
        message: str = "Error en servicio de IA",
        model: Optional[str] = None,
        **kwargs
    ):
        """
        Inicializa la excepción de IA.
        Initializes the AI exception.

        Args:
            message: Mensaje de error / Error message
            model: Modelo de IA que falló / AI model that failed
            **kwargs: Argumentos adicionales / Additional arguments
        """
        details = kwargs.pop("details", {})
        if model:
            details["model"] = model
        super().__init__(message, details=details, **kwargs)
        self.model = model


class AIServiceTimeoutError(AIServiceError):
    """Timeout en llamada a IA.
    Timeout in AI call."""

    def __init__(
        self,
        message: str = "Timeout en llamada a IA",
        timeout_seconds: Optional[int] = None,
        **kwargs
    ):
        """
        Inicializa la excepción de timeout.
        Initializes the timeout exception.

        Args:
            message: Mensaje de error / Error message
            timeout_seconds: Timeout en segundos / Timeout in seconds
            **kwargs: Argumentos adicionales / Additional arguments
        """
        details = kwargs.pop("details", {})
        if timeout_seconds:
            details["timeout_seconds"] = timeout_seconds
        super().__init__(message, details=details, **kwargs)
        self.timeout_seconds = timeout_seconds


class AIServiceRateLimitError(AIServiceError):
    """Excedido rate limit de IA.
    AI rate limit exceeded."""

    def __init__(
        self,
        message: str = "Excedido rate limit de IA",
        retry_after: Optional[int] = None,
        **kwargs
    ):
        """
        Inicializa la excepción de rate limit.
        Initializes the rate limit exception.

        Args:
            message: Mensaje de error / Error message
            retry_after: Segundos antes de reintentar / Seconds before retrying
            **kwargs: Argumentos adicionales / Additional arguments
        """
        details = kwargs.pop("details", {})
        if retry_after:
            details["retry_after"] = retry_after
        super().__init__(message, details=details, **kwargs)
        self.retry_after = retry_after


class DocumentParsingError(DocumentExtractionError):
    """Error al parsear documento.
    Error parsing document."""

    def __init__(
        self,
        message: str = "Error al parsear documento",
        file_type: Optional[str] = None,
        file_name: Optional[str] = None,
        **kwargs
    ):
        """
        Inicializa la excepción de parsing.
        Initializes the parsing exception.

        Args:
            message: Mensaje de error / Error message
            file_type: Tipo de archivo / File type
            file_name: Nombre del archivo / File name
            **kwargs: Argumentos adicionales / Additional arguments
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
    """Error específico al parsear PDF.
    Specific error parsing PDF."""

    def __init__(
        self,
        message: str = "Error al parsear PDF",
        page_number: Optional[int] = None,
        **kwargs
    ):
        """
        Inicializa la excepción de PDF.
        Initializes the PDF exception.

        Args:
            message: Mensaje de error / Error message
            page_number: Número de página que falló / Page number that failed
            **kwargs: Argumentos adicionales / Additional arguments
        """
        details = kwargs.pop("details", {})
        if page_number is not None:
            details["page_number"] = page_number
        kwargs["file_type"] = "PDF"
        super().__init__(message, details=details, **kwargs)
        self.page_number = page_number


class WordParsingError(DocumentParsingError):
    """Error específico al parsear Word.
    Specific error parsing Word."""

    def __init__(
        self,
        message: str = "Error al parsear Word",
        **kwargs
    ):
        """
        Inicializa la excepción de Word.
        Initializes the Word exception.

        Args:
            message: Mensaje de error / Error message
            **kwargs: Argumentos adicionales / Additional arguments
        """
        kwargs["file_type"] = "Word"
        super().__init__(message, **kwargs)


class ValidationError(DocumentExtractionError):
    """Error de validación de datos extraídos.
    Validation error for extracted data."""

    def __init__(
        self,
        message: str = "Error de validación",
        field: Optional[str] = None,
        value: Optional[Any] = None,
        **kwargs
    ):
        """
        Inicializa la excepción de validación.
        Initializes the validation exception.

        Args:
            message: Mensaje de error / Error message
            field: Campo que falló la validación / Field that failed validation
            value: Valor que falló la validación / Value that failed validation
            **kwargs: Argumentos adicionales / Additional arguments
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
    """Error cuando las caras de un documento son inconsistentes.
    Error when document faces are inconsistent."""

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
        Initializes the inconsistency exception.

        Args:
            message: Mensaje de error / Error message
            field: Campo inconsistente / Inconsistent field
            frontal_value: Valor de la cara frontal / Front face value
            back_value: Valor de la cara trasera / Back face value
            **kwargs: Argumentos adicionales / Additional arguments
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
