"""
Value Object para datos extraídos de un documento.
Encapsula la estructura de datos extraídos de la IA.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class ExtractionData:
    """
    Datos extraídos de un documento.

    Attributes:
        tipo_documento: Tipo de documento
        numero_documento: Número de documento
        nombres: Nombres completos
        apellidos: Apellidos completos
        fecha_nacimiento: Fecha de nacimiento
        sexo: Sexo (M/F)
        nacionalidad: Nacionalidad
        fecha_expedicion: Fecha de expedición (opcional)
        fecha_vencimiento: Fecha de vencimiento (opcional)
        lugar_expedicion: Lugar de expedición (opcional)
        lugar_nacimiento: Lugar de nacimiento (opcional)
        huella_digital: Huella digital (opcional)
        firma: Firma (opcional)
        codigo_qr: Código QR (opcional)
        datos_biometricos: Datos biométricos (opcional)
        grupo_sanguineo: Grupo sanguíneo (opcional)
        tipo_visa: Tipo de visa (opcional)
    """

    tipo_documento: str = ""
    numero_documento: str = ""
    nombres: str = ""
    apellidos: str = ""
    fecha_nacimiento: str = ""
    sexo: str = ""
    nacionalidad: str = ""
    fecha_expedicion: str = ""
    fecha_vencimiento: str = ""
    lugar_expedicion: str = ""
    lugar_nacimiento: str = ""
    huella_digital: str = ""
    firma: str = ""
    codigo_qr: str = ""
    datos_biometricos: str = ""
    grupo_sanguineo: str = ""
    tipo_visa: str = ""

    def to_dict(self) -> Dict[str, str]:
        """Convierte los datos a un diccionario."""
        return {
            "tipo_documento": self.tipo_documento,
            "numero_documento": self.numero_documento,
            "nombres": self.nombres,
            "apellidos": self.apellidos,
            "fecha_nacimiento": self.fecha_nacimiento,
            "sexo": self.sexo,
            "nacionalidad": self.nacionalidad,
            "fecha_expedicion": self.fecha_expedicion,
            "fecha_vencimiento": self.fecha_vencimiento,
            "lugar_expedicion": self.lugar_expedicion,
            "lugar_nacimiento": self.lugar_nacimiento,
            "huella_digital": self.huella_digital,
            "firma": self.firma,
            "codigo_qr": self.codigo_qr,
            "datos_biometricos": self.datos_biometricos,
            "grupo_sanguineo": self.grupo_sanguineo,
            "tipo_visa": self.tipo_visa
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExtractionData":
        """
        Crea una instancia desde un diccionario.

        Args:
            data: Diccionario con los datos extraídos

        Returns:
            Instancia de ExtractionData
        """
        return cls(
            tipo_documento=str(data.get("tipo_documento", "")),
            numero_documento=str(data.get("numero_documento", "")),
            nombres=str(data.get("nombres", "")),
            apellidos=str(data.get("apellidos", "")),
            fecha_nacimiento=str(data.get("fecha_nacimiento", "")),
            sexo=str(data.get("sexo", "")),
            nacionalidad=str(data.get("nacionalidad", "")),
            fecha_expedicion=str(data.get("fecha_expedicion", "")),
            fecha_vencimiento=str(data.get("fecha_vencimiento", "")),
            lugar_expedicion=str(data.get("lugar_expedicion", "")),
            lugar_nacimiento=str(data.get("lugar_nacimiento", "")),
            huella_digital=str(data.get("huella_digital", "")),
            firma=str(data.get("firma", "")),
            codigo_qr=str(data.get("codigo_qr", "")),
            datos_biometricos=str(data.get("datos_biometricos", "")),
            grupo_sanguineo=str(data.get("grupo_sanguineo", "")),
            tipo_visa=str(data.get("tipo_visa", ""))
        )

    def is_empty(self) -> bool:
        """
        Verifica si los datos están vacíos.

        Returns:
            True si todos los campos principales están vacíos
        """
        return not any([
            self.numero_documento.strip(),
            self.nombres.strip(),
            self.apellidos.strip()
        ])

    def has_required_fields(self) -> bool:
        """
        Verifica si tiene los campos obligatorios.

        Returns:
            True si todos los campos requeridos tienen valor
        """
        required_fields = [
            self.numero_documento.strip(),
            self.nombres.strip(),
            self.apellidos.strip(),
            self.fecha_nacimiento.strip(),
            self.sexo.strip(),
            self.nacionalidad.strip()
        ]
        return all(field for field in required_fields)

    def normalize(self) -> "ExtractionData":
        """
        Normaliza los valores (eliminar espacios, formatear fechas).

        Returns:
            Instancia normalizada
        """
        return ExtractionData(
            tipo_documento=self.tipo_documento.strip(),
            numero_documento=self.numero_documento.replace(" ", "").replace("-", ""),
            nombres=self.nombres.strip(),
            apellidos=self.apellidos.strip(),
            fecha_nacimiento=self._normalize_date(self.fecha_nacimiento),
            sexo=self.sexo.strip().upper(),
            nacionalidad=self.nacionalidad.strip(),
            fecha_expedicion=self._normalize_date(self.fecha_expedicion),
            fecha_vencimiento=self._normalize_date(self.fecha_vencimiento),
            lugar_expedicion=self.lugar_expedicion.strip(),
            lugar_nacimiento=self.lugar_nacimiento.strip(),
            huella_digital=self.huella_digital.strip(),
            firma=self.firma.strip(),
            codigo_qr=self.codigo_qr.strip(),
            datos_biometricos=self.datos_biometricos.strip(),
            grupo_sanguineo=self.grupo_sanguineo.strip(),
            tipo_visa=self.tipo_visa.strip()
        )

    @staticmethod
    def _normalize_date(date_str: str) -> str:
        """
        Normaliza el formato de una fecha.

        Args:
            date_str: Fecha en cualquier formato

        Returns:
            Fecha en formato DD/MM/YYYY o string original si no se puede normalizar
        """
        if not date_str:
            return ""

        date_str = date_str.strip()

        # Si ya está en formato DD/MM/YYYY, retornamos
        if "/" in date_str and len(date_str.split("/")) == 3:
            return date_str

        # Si está en formato YYYY-MM-DD, convertimos a DD/MM/YYYY
        if "-" in date_str and len(date_str.split("-")) == 3:
            parts = date_str.split("-")
            if len(parts[0]) == 4:  # Formato YYYY-MM-DD
                return f"{parts[2]}/{parts[1]}/{parts[0]}"

        return date_str
