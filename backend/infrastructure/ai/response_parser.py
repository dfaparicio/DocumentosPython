"""
Parser seguro de respuestas JSON de la IA.
Reemplaza las 3 instancias inseguras de `eval()`.
"""

import json
import logging
from typing import Any, Dict, Optional

from core.exceptions import AIServiceError

logger = logging.getLogger(__name__)


class JSONResponseParser:
    """Parser seguro de respuestas JSON de la IA."""

    def __init__(self, strict_mode: bool = True):
        """
        Inicializa el parser.

        Args:
            strict_mode: Si es True, lanza excepción en errores de parsing.
                         Si es False, retorna dict vacío en errores.
        """
        self.strict_mode = strict_mode

    def parse(self, response_text: str) -> Dict[str, Any]:
        """
        Parsea una respuesta de la IA a un diccionario de forma segura.

        Args:
            response_text: Texto de respuesta de la IA

        Returns:
            Diccionario parseado

        Raises:
            AIServiceError: Si el parsing falla y strict_mode es True
        """
        if not response_text:
            logger.warning("Respuesta vacía recibida de la IA")
            if self.strict_mode:
                raise AIServiceError("Respuesta vacía recibida de la IA")
            return {}

        # Limpiar el texto
        cleaned_text = self._clean_response(response_text)

        try:
            # Usar json.loads en lugar de eval()
            result = json.loads(cleaned_text)

            # Validar que el resultado sea un diccionario
            if not isinstance(result, dict):
                logger.error(
                    f"La respuesta no es un diccionario",
                    extra={"type": type(result).__name__}
                )
                if self.strict_mode:
                    raise AIServiceError(
                        "La respuesta de la IA no es un objeto JSON válido"
                    )
                return {}

            logger.debug("Respuesta JSON parseada exitosamente")
            return result

        except json.JSONDecodeError as e:
            logger.error(
                f"Error al parsear JSON de la IA",
                extra={
                    "error": str(e),
                    "response_snippet": response_text[:200]
                }
            )
            if self.strict_mode:
                raise AIServiceError(
                    f"Error al parsear respuesta JSON de la IA: {str(e)}",
                    details={"original_error": str(e)}
                )
            return {}

    def parse_with_validation(
        self,
        response_text: str,
        required_fields: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Parsea y valida la respuesta de la IA.

        Args:
            response_text: Texto de respuesta de la IA
            required_fields: Lista de campos requeridos que deben estar presentes

        Returns:
            Diccionario parseado y validado

        Raises:
            AIServiceError: Si el parsing falla o faltan campos requeridos
        """
        result = self.parse(response_text)

        # Validar campos requeridos
        if required_fields:
            missing_fields = [
                field for field in required_fields
                if field not in result
            ]
            if missing_fields:
                logger.warning(
                    f"Faltan campos requeridos en la respuesta",
                    extra={"missing_fields": missing_fields}
                )
                if self.strict_mode:
                    raise AIServiceError(
                        f"Faltan campos requeridos en la respuesta: {missing_fields}",
                        details={"missing_fields": missing_fields}
                    )
                # Agregar campos faltantes con valores vacíos
                for field in missing_fields:
                    result[field] = ""

        return result

    def _clean_response(self, response_text: str) -> str:
        """
        Limpia la respuesta de la IA antes de parsear.

        Args:
            response_text: Texto de respuesta original

        Returns:
            Texto limpio
        """
        # Eliminar espacios en blanco al inicio y final
        cleaned = response_text.strip()

        # Eliminar bloques de código markdown
        if cleaned.startswith("```json"):
            cleaned = cleaned.replace("```json", "", 1)
        elif cleaned.startswith("```"):
            cleaned = cleaned.replace("```", "", 1)

        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]

        # Eliminar espacios restantes
        cleaned = cleaned.strip()

        return cleaned

    def ensure_required_fields(
        self,
        data: Dict[str, Any],
        required_fields: list,
        optional_fields: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Asegura que todos los campos requeridos estén presentes en el resultado.

        Args:
            data: Diccionario de datos
            required_fields: Lista de campos requeridos
            optional_fields: Lista de campos opcionales (se agregan con valor vacío si faltan)

        Returns:
            Diccionario con todos los campos requeridos y opcionales
        """
        result = data.copy()

        # Asegurar campos requeridos
        for field in required_fields:
            if field not in result:
                logger.warning(f"Campo requerido faltante, usando valor vacío: {field}")
                result[field] = ""

        # Asegurar campos opcionales
        if optional_fields:
            for field in optional_fields:
                if field not in result:
                    result[field] = ""

        return result


# Instancia global del parser
_parser_instance: Optional[JSONResponseParser] = None


def get_parser(strict_mode: bool = True) -> JSONResponseParser:
    """
    Retorna la instancia singleton del parser.

    Args:
        strict_mode: Modo estricto del parser

    Returns:
        Instancia de JSONResponseParser
    """
    global _parser_instance
    if _parser_instance is None:
        _parser_instance = JSONResponseParser(strict_mode=strict_mode)
    return _parser_instance


def parse_response(response_text: str, strict_mode: bool = True) -> Dict[str, Any]:
    """
    Función de conveniencia para parsear una respuesta.

    Args:
        response_text: Texto de respuesta de la IA
        strict_mode: Si es True, lanza excepción en errores

    Returns:
        Diccionario parseado
    """
    parser = get_parser(strict_mode=strict_mode)
    return parser.parse(response_text)
