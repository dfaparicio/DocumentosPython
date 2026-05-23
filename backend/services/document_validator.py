"""
Validador de consistencia de documentos.
Valida que las caras de un documento sean consistentes entre sí.

Document consistency validator.
Validates that the faces of a document are consistent with each other.
"""

from typing import Dict, List, Optional, Tuple
import re


class ValidationError:
    """Representa un error de validación encontrado.
    Represents a validation error found."""

    def __init__(self, field: str, message: str, severity: str = "warning"):
        """
        Inicializa un error de validación.
        Initializes a validation error.

        Args:
            field: Campo donde ocurrió el error / Field where the error occurred
            message: Mensaje descriptivo del error / Descriptive error message
            severity: Severidad del error ("error", "warning", "info") / Error severity ("error", "warning", "info")
        """
        self.field = field
        self.message = message
        self.severity = severity

    def to_dict(self) -> Dict[str, str]:
        """Convierte el error a un diccionario.
        Converts the error to a dictionary."""
        return {
            "field": self.field,
            "message": self.message,
            "severity": self.severity
        }


class ValidationResult:
    """Resultado de la validación de un documento.
    Result of document validation."""

    def __init__(self):
        """Inicializa el resultado de validación.
        Initializes the validation result."""
        self.is_valid: bool = True
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []

    def add_error(self, field: str, message: str):
        """Agrega un error al resultado.
        Adds an error to the result."""
        self.is_valid = False
        self.errors.append(ValidationError(field, message, "error"))

    def add_warning(self, field: str, message: str):
        """Agrega una advertencia al resultado.
        Adds a warning to the result."""
        self.warnings.append(ValidationError(field, message, "warning"))

    def to_dict(self) -> Dict[str, any]:
        """Convierte el resultado a un diccionario.
        Converts the result to a dictionary."""
        return {
            "is_valid": self.is_valid,
            "errors": [e.to_dict() for e in self.errors],
            "warnings": [w.to_dict() for w in self.warnings]
        }


class DocumentValidator:
    """
    Validador de documentos colombianos.
    Colombian document validator.
    """

    def __init__(self):
        """Inicializa el validador de documentos.
        Initializes the document validator."""
        # Patrón para validar números de documento colombianos
        # Pattern to validate Colombian document numbers
        self.doc_number_pattern = re.compile(r'^[\dA-Za-z-]+$')

        # Patrones para validar fechas
        # Patterns to validate dates
        self.date_pattern_ddmmyyyy = re.compile(r'^\d{2}/\d{2}/\d{4}$')
        self.date_pattern_yyyymmdd = re.compile(r'^\d{4}-\d{2}-\d{2}$')

        # Valores válidos para sexo
        # Valid sex values
        self.valid_sexo_values = ["M", "F", "Masculino", "Femenino", ""]

    def validate_document_consistency(self,
                                      frontal_data: Optional[Dict[str, str]],
                                      trasera_data: Optional[Dict[str, str]],
                                      document_type: str) -> ValidationResult:
        """
        Valida la consistencia entre las caras frontal y trasera de un documento.
        Validates consistency between the front and back faces of a document.

        Args:
            frontal_data: Datos de la cara frontal / Front face data
            trasera_data: Datos de la cara trasera / Back face data
            document_type: Tipo de documento / Document type

        Returns:
            ValidationResult con los errores y advertencias encontrados / ValidationResult with errors and warnings found
        """
        result = ValidationResult()

        # Si no hay datos de ninguna cara, no podemos validar
        # If there is no data from any face, we cannot validate
        if not frontal_data and not trasera_data:
            result.add_error("general", "No hay datos para validar")
            return result

        # Validamos consistencia del número de documento
        # We validate document number consistency
        if frontal_data and trasera_data:
            self._validate_document_number_consistency(frontal_data, trasera_data, result)

        # Validamos consistencia del tipo de documento
        # We validate document type consistency
        if frontal_data and trasera_data:
            self._validate_document_type_consistency(frontal_data, trasera_data, result)

        # Validamos los datos individuales
        # We validate individual data
        if frontal_data:
            self._validate_single_face_data(frontal_data, document_type, result, "frontal")

        if trasera_data:
            self._validate_single_face_data(trasera_data, document_type, result, "trasera")

        return result

    def validate_single_document(self,
                                 data: Optional[Dict[str, str]],
                                 document_type: str) -> ValidationResult:
        """
        Valida un documento de una sola cara (ej: pasaporte).
        Validates a single-face document (e.g.: passport).

        Args:
            data: Datos del documento / Document data
            document_type: Tipo de documento / Document type

        Returns:
            ValidationResult con los errores y advertencias encontrados / ValidationResult with errors and warnings found
        """
        result = ValidationResult()

        if not data:
            result.add_error("general", "No hay datos para validar")
            return result

        self._validate_single_face_data(data, document_type, result, "unico")

        return result

    def _validate_document_number_consistency(self,
                                             frontal_data: Dict[str, str],
                                             trasera_data: Dict[str, str],
                                             result: ValidationResult):
        """
        Valida que el número de documento sea consistente entre caras.
        Validates that the document number is consistent between faces.

        Args:
            frontal_data: Datos de la cara frontal / Front face data
            trasera_data: Datos de la cara trasera / Back face data
            result: ValidationResult para agregar errores / ValidationResult to add errors
        """
        front_num = frontal_data.get("numero_documento", "").strip()
        back_num = trasera_data.get("numero_documento", "").strip()

        if front_num and back_num:
            # Limpiamos los números de espacios y guiones para comparar
            # We clean the numbers of spaces and hyphens for comparison
            front_num_clean = front_num.replace(" ", "").replace("-", "")
            back_num_clean = back_num.replace(" ", "").replace("-", "")

            if front_num_clean and back_num_clean and front_num_clean != back_num_clean:
                result.add_error(
                    "numero_documento",
                    f"Los números de documento no coinciden: Frontal='{front_num}', Trasera='{back_num}'"
                )
        elif front_num and not back_num:
            result.add_warning("numero_documento", "Número de documento no encontrado en la cara trasera")
        elif not front_num and back_num:
            result.add_warning("numero_documento", "Número de documento no encontrado en la cara frontal")

    def _validate_document_type_consistency(self,
                                           frontal_data: Dict[str, str],
                                           trasera_data: Dict[str, str],
                                           result: ValidationResult):
        """
        Valida que el tipo de documento sea consistente entre caras.
        Validates that the document type is consistent between faces.

        Args:
            frontal_data: Datos de la cara frontal / Front face data
            trasera_data: Datos de la cara trasera / Back face data
            result: ValidationResult para agregar errores / ValidationResult to add errors
        """
        front_type = frontal_data.get("tipo_documento", "").strip()
        back_type = trasera_data.get("tipo_documento", "").strip()

        if front_type and back_type:
            if front_type != back_type:
                result.add_warning(
                    "tipo_documento",
                    f"Los tipos de documento difieren: Frontal='{front_type}', Trasera='{back_type}'"
                )

    def _validate_single_face_data(self,
                                   data: Dict[str, str],
                                   document_type: str,
                                   result: ValidationResult,
                                   face_label: str):
        """
        Valida los datos de una sola cara.
        Validates the data of a single face.

        Args:
            data: Datos de la cara / Face data
            document_type: Tipo de documento / Document type
            result: ValidationResult para agregar errores / ValidationResult to add errors
            face_label: Etiqueta de la cara (para mensajes de error) / Face label (for error messages)
        """
        # Validar número de documento
        # Validate document number
        self._validate_document_number(data, result)

        # Validar nombres y apellidos
        # Validate names and surnames
        self._validate_names(data, result)

        # Validar fecha de nacimiento
        # Validate date of birth
        self._validate_date(data, "fecha_nacimiento", result)

        # Validar sexo
        # Validate sex
        self._validate_sexo(data, result)

        # Validaciones específicas por tipo de documento
        # Specific validations by document type
        if document_type == "cedula_extranjeria":
            self._validate_date(data, "fecha_vencimiento", result)
            self._validate_date(data, "fecha_expedicion", result)

        elif document_type == "pasaporte":
            self._validate_date(data, "fecha_vencimiento", result)
            self._validate_date(data, "fecha_expedicion", result)

    def _validate_document_number(self, data: Dict[str, str], result: ValidationResult):
        """
        Valida el formato del número de documento.
        Validates the document number format.

        Args:
            data: Datos del documento / Document data
            result: ValidationResult para agregar errores / ValidationResult to add errors
        """
        doc_num = data.get("numero_documento", "").strip()

        if not doc_num:
            result.add_error("numero_documento", "Número de documento no encontrado")
        elif len(doc_num) < 5:
            result.add_error("numero_documento", f"Número de documento muy corto: '{doc_num}'")
        elif not self.doc_number_pattern.match(doc_num):
            result.add_error("numero_documento", f"Número de documento con caracteres inválidos: '{doc_num}'")

    def _validate_names(self, data: Dict[str, str], result: ValidationResult):
        """
        Valida los nombres y apellidos.
        Validates first names and surnames.

        Args:
            data: Datos del documento / Document data
            result: ValidationResult para agregar errores / ValidationResult to add errors
        """
        nombres = data.get("nombres", "").strip()
        apellidos = data.get("apellidos", "").strip()

        if not nombres:
            result.add_warning("nombres", "Nombres no encontrados")

        if not apellidos:
            result.add_warning("apellidos", "Apellidos no encontrados")

    def _validate_date(self, data: Dict[str, str], field_name: str, result: ValidationResult):
        """
        Valida el formato de una fecha.
        Validates the format of a date.

        Args:
            data: Datos del documento / Document data
            field_name: Nombre del campo de fecha / Date field name
            result: ValidationResult para agregar errores / ValidationResult to add errors
        """
        date_str = data.get(field_name, "").strip()

        if not date_str:
            return  # Campo opcional / Optional field

        # Validamos que tenga un formato reconocido
        # We validate that it has a recognized format
        if not (self.date_pattern_ddmmyyyy.match(date_str) or
                self.date_pattern_yyyymmdd.match(date_str)):
            result.add_warning(field_name, f"Formato de fecha no reconocido: '{date_str}'")

    def _validate_sexo(self, data: Dict[str, str], result: ValidationResult):
        """
        Valida el campo sexo.
        Validates the sex field.

        Args:
            data: Datos del documento / Document data
            result: ValidationResult para agregar errores / ValidationResult to add errors
        """
        sexo = data.get("sexo", "").strip()

        if sexo and sexo not in self.valid_sexo_values:
            result.add_warning("sexo", f"Valor de sexo no reconocido: '{sexo}'")

    def is_two_face_document(self, document_type: str) -> bool:
        """
        Determina si un tipo de documento tiene 2 caras.
        Determines if a document type has 2 faces.

        Args:
            document_type: Tipo de documento / Document type

        Returns:
            True si tiene 2 caras, False si tiene 1 sola cara / True if it has 2 faces, False if it has only 1 face
        """
        two_face_types = [
            "cedula_ciudadania_vieja",
            "cedula_ciudadania_nueva",
            "cedula_digital",
            "tarjeta_identidad",
            "cedula_extranjeria"
        ]
        return document_type in two_face_types


# Instancia global del validador para reutilizar
# Global validator instance for reuse
_validator_instance = None


def get_validator() -> DocumentValidator:
    """
    Retorna la instancia global del validador (singleton pattern).
    Returns the global validator instance (singleton pattern).

    Returns:
        Instancia de DocumentValidator / DocumentValidator instance
    """
    global _validator_instance
    if _validator_instance is None:
        _validator_instance = DocumentValidator()
    return _validator_instance


def validate_and_merge(frontal_data: Optional[Dict[str, str]],
                      trasera_data: Optional[Dict[str, str]],
                      document_type: str,
                      validator: Optional[DocumentValidator] = None) -> Tuple[Dict[str, str], ValidationResult]:
    """
    Valida y combina los datos de un documento.
    Validates and merges document data.

    Args:
        frontal_data: Datos de la cara frontal / Front face data
        trasera_data: Datos de la cara trasera / Back face data
        document_type: Tipo de documento / Document type
        validator: Instancia del validador (opcional) / Validator instance (optional)

    Returns:
        Tupla (datos_combinados, resultado_validacion) / Tuple (combined_data, validation_result)
    """
    if validator is None:
        validator = get_validator()

    # Validamos consistencia
    # We validate consistency
    validation_result = validator.validate_document_consistency(
        frontal_data, trasera_data, document_type
    )

    # Combinamos los datos
    # We merge the data
    from services.data_merger import merge_face_data
    combined_data = merge_face_data(frontal_data, trasera_data, document_type)

    return combined_data, validation_result
