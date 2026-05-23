"""
Esquema de datos para validar la información extraída de las cédulas
Usamos Pydantic para asegurar que los datos tengan el formato correcto

Data schema to validate information extracted from ID cards.
We use Pydantic to ensure data has the correct format.
"""

from pydantic import BaseModel, Field
from typing import Optional

class StudentData(BaseModel):
    """
    Modelo que define la estructura de los datos que extraeremos de cada cédula.
    Incluye validaciones para asegurar que la información sea correcta.

    Model that defines the structure of the data we will extract from each ID card.
    Includes validations to ensure the information is correct.
    """

    # Nombres de la persona
    # Person's first names
    # Optional significa que el campo puede estar vacío si la IA no lo encuentra
    # Optional means the field can be empty if the AI does not find it
    nombres: Optional[str] = Field(
        default="",
        description="Nombres completos de la persona"
    )

    # Apellidos de la persona
    # Person's last names
    apellidos: Optional[str] = Field(
        default="",
        description="Apellidos completos de la persona"
    )

    # Número de documento (cédula)
    # Document number (ID card)
    numero_documento: Optional[str] = Field(
        default="",
        description="Número de cédula de identidad"
    )

    # Fecha de nacimiento
    # Date of birth
    fecha_nacimiento: Optional[str] = Field(
        default="",
        description="Fecha de nacimiento en formato DD/MM/AAAA"
    )

    class Config:
        """
        Configuración adicional del modelo.
        Usamos esto para generar ejemplos en la documentación de la API.

        Additional model configuration.
        We use this to generate examples in the API documentation.
        """
        json_schema_extra = {
            "example": {
                "nombres": "Juan Carlos",
                "apellidos": "Pérez López",
                "numero_documento": "1234567890",
                "fecha_nacimiento": "15/03/1990"
            }
        }

class ExtractionResponse(BaseModel):
    """
    Modelo de respuesta cuando el sistema termina de procesar.
    Le avisa al usuario si todo salió bien o si hubo algún problema.

    Response model when the system finishes processing.
    Notifies the user whether everything went well or if there was a problem.
    """

    estado: str = Field(
        ...,
        description="Estado del proceso: éxito o error"
    )

    mensaje: str = Field(
        ...,
        description="Mensaje que explica qué pasó"
    )

    cantidad_procesada: int = Field(
        default=0,
        description="Cantidad de cédulas que se procesaron"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "estado": "exito",
                "mensaje": "Se procesaron 5 cédulas correctamente",
                "cantidad_procesada": 5
            }
        }
