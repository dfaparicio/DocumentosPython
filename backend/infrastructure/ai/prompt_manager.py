"""
Gestor de prompts para la IA.
Consolida los prompts de document_prompts.py y añade caché.
"""

import logging
from typing import Optional

from config import get_settings
from application.services.interfaces.ai_provider import PromptType

logger = logging.getLogger(__name__)


class PromptManager:
    """
    Gestor de prompts para la IA.

    Centraliza todos los prompts usados para interactuar con Gemini
    y los mantiene en caché para evitar reconstrucciones.
    """

    # Prompts de clasificación
    _CLASSIFICATION_PROMPT = """
Analiza esta imagen y determina:

1. ¿Qué tipo de cara es?
   - FRONTAL: Tiene foto de persona, número de documento, nombres completos
   - TRASERA: Tiene firma, huella digital, fecha de expedición, lugar
   - COMPLETO: Contiene toda la información en una sola cara (como pasaporte o contraseña)
   - MIXTO: Contiene dos caras de un documento (una frontal y una trasera)

2. ¿Qué tipo de documento colombiano es?
   - CÉDULA DE CIUDADANÍA VIEJA (amarilla/rosada, diseño antiguo)
   - CÉDULA DE CIUDADANÍA NUEVA (diseño moderno)
   - CÉDULA DIGITAL (con código QR)
   - TARJETA DE IDENTIDAD (para menores)
   - CÉDULA DE EXTRANJERÍA (para extranjeros)
   - PASAPORTE (documento de viaje)
   - PERMISO PPT (permiso temporal)
   - OTRO (cualquier otro documento)

3. ¿Qué características tiene?
   - Tiene foto (SÍ/NO)
   - Tiene firma (SÍ/NO)
   - Tiene huella digital (SÍ/NO)
   - Tiene número de documento (SÍ/NO)

Responde en formato JSON:
{
    "face_type": "FRONTAL" | "TRASERA" | "COMPLETO" | "MIXTO",
    "document_type": "cedula_ciudadania_vieja" | "cedula_ciudadania_nueva" | "cedula_digital" | "tarjeta_identidad" | "cedula_extranjeria" | "pasaporte" | "ppt" | "otro",
    "confidence": número entre 0.0 y 1.0,
    "features": {
        "has_photo": true/false,
        "has_signature": true/false,
        "has_fingerprint": true/false,
        "has_number": true/false
    }
}
"""

    # Prompt para detectar páginas mixtas
    _MIXED_DETECTION_PROMPT = """
Analiza esta imagen y determina si contiene DOS caras de un documento colombiano.

Busca:
- Dos secciones claramente divididas (una arriba, otra abajo)
- Elementos de AMBOS: foto Y firma/huella
- Dos números de documento diferentes
- Texto que se repite o que indica dos lados
- Dos encabezados o títulos de documento

Responde SOLO con "SI" o "NO".
"""

    # Prompt para obtener coordenadas de división
    _SPLIT_COORDINATES_PROMPT = """
Analiza esta imagen que contiene DOS caras de un documento colombiano.

Necesito que me des las COORDENADAS de ambas caras para dividirlas.

Responde en formato JSON:
{
    "cara_1": {
        "y_inicio": número de píxel desde arriba,
        "y_fin": número de píxel hasta abajo,
        "x_inicio": número de píxel desde izquierda,
        "x_fin": número de píxel hasta derecha,
        "descripcion": "FRONTAL" o "TRASERA"
    },
    "cara_2": {
        "y_inicio": número de píxel desde arriba,
        "y_fin": número de píxel hasta abajo,
        "x_inicio": número de píxel desde izquierda,
        "x_fin": número de píxel hasta derecha,
        "descripcion": "FRONTAL" o "TRASERA"
    }
}

Considera:
- Cara 1 es la que está arriba
- Cara 2 es la que está abajo
- Usa coordenadas en píxeles
- x_inicio siempre debe ser 0 (borde izquierdo)
- x_fin debe ser el ancho total de la imagen
- Identifica si cada cara es FRONTAL o TRASERA
"""

    def __init__(self):
        """Inicializa el gestor de prompts."""
        self._cache = {}

        # Mapeo interno de tipos de prompt a funciones generadoras
        self._prompt_generators = {
            PromptType.CLASSIFICATION: self._get_classification_prompt,
            PromptType.MIXED_DETECTION: self._get_mixed_detection_prompt,
            PromptType.SPLIT_COORDINATES: self._get_split_coordinates_prompt
        }

        logger.info("PromptManager inicializado")

    def get_prompt(self, prompt_type: PromptType, **kwargs) -> str:
        """
        Obtiene un prompt específico.

        Args:
            prompt_type: Tipo de prompt
            **kwargs: Parámetros adicionales para prompts parametrizados

        Returns:
            Prompt solicitado
        """
        # Intentar obtener del caché
        cache_key = f"{prompt_type.value}:{str(sorted(kwargs.items()))}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Generar prompt
        if prompt_type in self._prompt_generators:
            prompt = self._prompt_generators[prompt_type](**kwargs)
        else:
            logger.warning(f"Tipo de prompt desconocido: {prompt_type}")
            prompt = ""

        # Cachear
        self._cache[cache_key] = prompt
        return prompt

    def get_extraction_prompt(self, document_type: str, face_type: str) -> str:
        """
        Genera un prompt específico para extracción de datos.

        Args:
            document_type: Tipo de documento
            face_type: Tipo de cara (frontal, trasera, completo)

        Returns:
            Prompt específico para extracción
        """
        # Mapear tipos a nombres legibles
        type_names = {
            "cedula_ciudadania_vieja": "Cédula de Ciudadanía Vieja",
            "cedula_ciudadania_nueva": "Cédula de Ciudadanía Nueva",
            "cedula_digital": "Cédula Digital",
            "tarjeta_identidad": "Tarjeta de Identidad",
            "cedula_extranjeria": "Cédula de Extranjería",
            "pasaporte": "Pasaporte",
            "ppt": "Permiso PPT",
            "otro": "Otro Documento"
        }

        type_name = type_names.get(document_type, document_type.replace("_", " ").title())

        if face_type == "completo":
            return f"""
Analiza este {type_name}. Extrae TODA la información visible en esta única cara.

Extrae:
1. Tipo de Documento (ej: "{type_name}")
2. Número de Documento (si es visible)
3. Nombres completos
4. Apellidos completos
5. Fecha de Nacimiento
6. Sexo (M/F)
7. Nacionalidad
8. Fecha de Expedición (si es visible)
9. Fecha de Vencimiento (si es visible)
10. Lugar de Expedición (si es visible)
11. Lugar de Nacimiento (si es visible)
12. Huella digital (indicar "PRESENTE" o "AUSENTE")
13. Firma (indicar "PRESENTE" o "AUSENTE")
14. Código QR (indicar "PRESENTE" o "AUSENTE")

IMPORTANTE:
- Si un campo no está visible, déjalo como string vacío ""
- Responde en formato JSON válido
- No agregues texto fuera del JSON

Ejemplo:
{{"tipo_documento": "{type_name}", "numero_documento": "12345678", "nombres": "Juan Carlos", "apellidos": "Pérez López", "fecha_nacimiento": "15/03/1990", "sexo": "M", "nacionalidad": "Colombiana", "fecha_expedicion": "", "fecha_vencimiento": "", "lugar_expedicion": "", "lugar_nacimiento": "", "huella_digital": "", "firma": "", "codigo_qr": ""}}
"""

        elif face_type == "frontal":
            return f"""
Analiza esta CARA FRONTAL de un {type_name}. Extrae SOLO la información visible en ESTA cara.

NO extraigas datos que suelen estar en la cara trasera:
- NO busques firma
- NO busques huella digital
- NO busques lugar de expedición

Extrae:
1. Tipo de Documento (ej: "{type_name}")
2. Número de Documento (el número que aparece en esta cara)
3. Nombres completos (si son visibles)
4. Apellidos completos (si son visibles)
5. Fecha de Nacimiento (si es visible)
6. Sexo (M/F si es visible)
7. Nacionalidad (si es visible)

IMPORTANTE:
- Si un campo no está visible, déjalo como string vacío ""
- Responde en formato JSON válido
- No agregues texto fuera del JSON

Ejemplo:
{{"tipo_documento": "{type_name}", "numero_documento": "12345678", "nombres": "Juan Carlos", "apellidos": "Pérez López", "fecha_nacimiento": "15/03/1990", "sexo": "M", "nacionalidad": "Colombiana"}}
"""

        elif face_type == "trasera":
            return f"""
Analiza esta CARA TRASERA de un {type_name}. Extrae la información complementaria que aparece aquí.

Extrae:
1. Tipo de Documento (ej: "{type_name}")
2. Número de Documento (para verificar que coincida con frontal)
3. Fecha de Expedición (si es visible)
4. Lugar de Expedición (ej: "Bogotá D.C." si es visible)
5. Huella digital (indicar "PRESENTE" o "AUSENTE")
6. Firma (indicar "PRESENTE" o "AUSENTE")
7. Datos biométricos adicionales (si hay alguno visible, como "CHIP" o "QR")
8. Fecha de Vencimiento (si es visible, muy importante para cédulas de extranjería)

IMPORTANTE:
- NO vuelvas a extraer nombres/apellidos (ya están en la frontal)
- Si un campo no está visible, déjalo como string vacío ""
- Responde en formato JSON válido
- No agregues texto fuera del JSON

Ejemplo:
{{"tipo_documento": "{type_name}", "numero_documento": "12345678", "fecha_expedicion": "10/01/2020", "lugar_expedicion": "Bogotá D.C.", "huella_digital": "PRESENTE", "firma": "PRESENTE", "datos_biometricos": "", "fecha_vencimiento": ""}}
"""

        else:
            logger.warning(f"Tipo de cara desconocido: {face_type}")
            return ""

    def _get_classification_prompt(self) -> str:
        """Retorna el prompt de clasificación."""
        return self._CLASSIFICATION_PROMPT

    def _get_mixed_detection_prompt(self) -> str:
        """Retorna el prompt de detección de páginas mixtas."""
        return self._MIXED_DETECTION_PROMPT

    def _get_split_coordinates_prompt(self) -> str:
        """Retorna el prompt de coordenadas de división."""
        return self._SPLIT_COORDINATES_PROMPT

    def clear_cache(self) -> None:
        """Limpia el caché de prompts."""
        self._cache.clear()
        logger.info("Caché de prompts limpiado")


# Instancia global del gestor de prompts
_prompt_manager_instance: Optional[PromptManager] = None


def get_prompt_manager() -> PromptManager:
    """
    Retorna la instancia singleton del gestor de prompts.

    Returns:
        Instancia de PromptManager
    """
    global _prompt_manager_instance
    if _prompt_manager_instance is None:
        _prompt_manager_instance = PromptManager()
    return _prompt_manager_instance
