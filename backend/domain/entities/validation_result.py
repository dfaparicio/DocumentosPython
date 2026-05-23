"""
Entidades de validación del dominio.
Representa resultados de validación de documentos.

Domain validation entities.
Represents document validation results.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class Severity(Enum):
    """Severidad de un error de validación.
    Severity of a validation error."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationErrorItem:
    """
    Representa un error de validación individual.
    Represents an individual validation error.

    Attributes:
        field: Campo donde ocurrió el error / Field where the error occurred
        message: Mensaje descriptivo del error / Descriptive error message
        severity: Severidad del error / Error severity
        value: Valor que causó el error (opcional) / Value that caused the error (optional)
    """

    field: str
    message: str
    severity: Severity = Severity.WARNING
    value: Optional[Any] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el error a un diccionario.
        Converts the error to a dictionary."""
        result = {
            "field": self.field,
            "message": self.message,
            "severity": self.severity.value
        }
        if self.value is not None:
            result["value"] = str(self.value)
        return result

    @classmethod
    def error(cls, field: str, message: str, value: Optional[Any] = None) -> "ValidationErrorItem":
        """Crea un error de severidad ERROR.
        Creates an error of ERROR severity."""
        return cls(field=field, message=message, severity=Severity.ERROR, value=value)

    @classmethod
    def warning(cls, field: str, message: str, value: Optional[Any] = None) -> "ValidationErrorItem":
        """Crea un error de severidad WARNING.
        Creates an error of WARNING severity."""
        return cls(field=field, message=message, severity=Severity.WARNING, value=value)

    @classmethod
    def info(cls, field: str, message: str, value: Optional[Any] = None) -> "ValidationErrorItem":
        """Crea un error de severidad INFO.
        Creates an error of INFO severity."""
        return cls(field=field, message=message, severity=Severity.INFO, value=value)


@dataclass
class ValidationResult:
    """
    Resultado de la validación de un documento.
    Result of document validation.

    Attributes:
        is_valid: Indica si el documento es válido (sin errores) / Indicates if the document is valid (no errors)
        errors: Lista de errores de validación / List of validation errors
        warnings: Lista de advertencias / List of warnings
        info: Lista de información adicional / List of additional information
    """

    is_valid: bool = True
    errors: List[ValidationErrorItem] = field(default_factory=list)
    warnings: List[ValidationErrorItem] = field(default_factory=list)
    info: List[ValidationErrorItem] = field(default_factory=list)

    def add_error(
        self,
        field: str,
        message: str,
        value: Optional[Any] = None
    ) -> None:
        """
        Agrega un error al resultado.
        Adds an error to the result.

        Args:
            field: Campo donde ocurrió el error / Field where the error occurred
            message: Mensaje descriptivo / Descriptive message
            value: Valor que causó el error / Value that caused the error
        """
        self.is_valid = False
        self.errors.append(ValidationErrorItem.error(field, message, value))

    def add_warning(
        self,
        field: str,
        message: str,
        value: Optional[Any] = None
    ) -> None:
        """
        Agrega una advertencia al resultado.
        Adds a warning to the result.

        Args:
            field: Campo donde ocurrió la advertencia / Field where the warning occurred
            message: Mensaje descriptivo / Descriptive message
            value: Valor relacionado / Related value
        """
        self.warnings.append(ValidationErrorItem.warning(field, message, value))

    def add_info(
        self,
        field: str,
        message: str,
        value: Optional[Any] = None
    ) -> None:
        """
        Agrega información al resultado.
        Adds information to the result.

        Args:
            field: Campo relacionado / Related field
            message: Mensaje descriptivo / Descriptive message
            value: Valor relacionado / Related value
        """
        self.info.append(ValidationErrorItem.info(field, message, value))

    def merge(self, other: "ValidationResult") -> None:
        """
        Fusiona otro resultado de validación con este.
        Merges another validation result with this one.

        Args:
            other: Otro resultado de validación / Another validation result
        """
        if not other.is_valid:
            self.is_valid = False
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        self.info.extend(other.info)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte el resultado a un diccionario.
        Converts the result to a dictionary.

        Returns:
            Diccionario con el resultado de validación / Dictionary with the validation result
        """
        return {
            "is_valid": self.is_valid,
            "errors": [error.to_dict() for error in self.errors],
            "warnings": [warning.to_dict() for warning in self.warnings],
            "info": [info_item.to_dict() for info_item in self.info]
        }

    @property
    def error_count(self) -> int:
        """Retorna el número de errores.
        Returns the number of errors."""
        return len(self.errors)

    @property
    def warning_count(self) -> int:
        """Retorna el número de advertencias.
        Returns the number of warnings."""
        return len(self.warnings)

    @property
    def has_errors(self) -> bool:
        """Retorna True si hay errores.
        Returns True if there are errors."""
        return len(self.errors) > 0

    @property
    def has_warnings(self) -> bool:
        """Retorna True si hay advertencias.
        Returns True if there are warnings."""
        return len(self.warnings) > 0
