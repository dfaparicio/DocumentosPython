"""
Paquete de infraestructura.
Contiene implementaciones concretas de interfaces definidas en la capa de aplicación.
"""

from .ai.response_parser import JSONResponseParser, get_parser, parse_response

__all__ = [
    "JSONResponseParser",
    "get_parser",
    "parse_response"
]
