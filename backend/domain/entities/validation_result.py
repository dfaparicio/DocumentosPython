"""
Entidades de validación del dominio.
Representa resultados de validación de documentos.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class Severity(Enum):
    """Severidad de un error de validación."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationErrorItem:
    """
    Representa un error de validación individual.

    Attributes:
        field: Campo donde ocurrió el error
        message: Mensaje descriptivo del error
        severity: Severidad del error
        value: Valor que causó el error (opcional)
    """

    field: str
    message: str
    severity: Severity = Severity.WARNING
    value: Optional[Any] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el error a un diccionario."""
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
        """Crea un error de severidad ERROR."""
        return cls(field=field, message=message, severity=Severity.ERROR, value=value)

    @classmethod
    def warning(cls, field: str, message: str, value: Optional[Any] = None) -> "ValidationErrorItem":
        """Crea un error de severidad WARNING."""
        return cls(field=field, message=message, severity=Severity.WARNING, value=value)

    @classmethod
    def info(cls, field: str, message: str, value: Optional[Any] = None) -> "ValidationErrorItem":
        """Crea un error de severidad INFO."""
        return cls(field=field, message=message, severity=Severity.INFO, value=value)


@dataclass
class ValidationResult:
    """
    Resultado de la validación de un documento.

    Attributes:
        is_valid: Indica si el documento es válido (sin errores)
        errors: Lista de errores de validación
        warnings: Lista de advertencias
        info: Lista de información adicional
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

        Args:
            field: Campo donde ocurrió el error
            message: Mensaje descriptivo
            value: Valor que causó el error
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

        Args:
            field: Campo donde ocurrió la advertencia
            message: Mensaje descriptivo
            value: Valor relacionado
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

        Args:
            field: Campo relacionado
            message: Mensaje descriptivo
            value: Valor relacionado
        """
        self.info.append(ValidationErrorItem.info(field, message, value))

    def merge(self, other: "ValidationResult") -> None:
        """
        Fusiona otro resultado de validación con este.

        Args:
            other: Otro resultado de validación
        """
        if not other.is_valid:
            self.is_valid = False
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        self.info.extend(other.info)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte el resultado a un diccionario.

        Returns:
            Diccionario con el resultado de validación
        """
        return {
            "is_valid": self.is_valid,
            "errors": [error.to_dict() for error in self.errors],
            "warnings": [warning.to_dict() for warning in self.warnings],
            "info": [info_item.to_dict() for info_item in self.info]
        }

    @property
    def error_count(self) -> int:
        """Retorna el número de errores."""
        return len(self.errors)

    @property
    def warning_count(self) -> int:
        """Retorna el número de advertencias."""
        return len(self.warnings)

    @property
    def has_errors(self) -> bool:
        """Retorna True si hay errores."""
        return len(self.errors) > 0

    @property
    def has_warnings(self) -> bool:
        """Retorna True si hay advertencias."""
        return len(self.warnings) > 0
