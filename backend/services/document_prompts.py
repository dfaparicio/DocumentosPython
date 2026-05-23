"""
Prompts específicos para extracción de datos de documentos colombianos.
Cada prompt está optimizado para un tipo de documento y tipo de cara específicos.

Specific prompts for data extraction from Colombian documents.
Each prompt is optimized for a specific document type and face type.
"""

from typing import Dict, List

DOCUMENT_PROMPTS = {
    # ========== CÉDULA DE CIUDADANÍA VIEJA ==========
    # ========== OLD CITIZENSHIP CARD ==========
    "cedula_ciudadania_vieja_frontal": """
    Analiza esta CARA FRONTAL de una CÉDULA DE CIUDADANÍA COLOMBIANA (versión antigua, amarilla/rosada con foto en la izquierda).
    Extrae SOLO la información visible en ESTA cara.

    NO extraigas datos que suelen estar en la cara trasera:
    - NO busques firma
    - NO busques huella digital
    - NO busques lugar de expedición

    Extrae:
    1. Tipo de Documento (ej: "Cédula de Ciudadanía Vieja")
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
    - Observa bien los datos en el formato antiguo de cédulas

    Ejemplo:
    {"tipo_documento": "Cédula de Ciudadanía Vieja", "numero_documento": "12345678", "nombres": "Juan Carlos", "apellidos": "Pérez López", "fecha_nacimiento": "15/03/1990", "sexo": "M", "nacionalidad": "Colombiana"}
    """,

    "cedula_ciudadania_vieja_trasera": """
    Analiza esta CARA TRASERA de una CÉDULA DE CIUDADANÍA COLOMBIANA (versión antigua).
    Extrae la información complementaria que aparece aquí.

    Extrae:
    1. Tipo de Documento (ej: "Cédula de Ciudadanía Vieja")
    2. Número de Documento (para verificar que coincida con frontal)
    3. Fecha de Expedición (si es visible)
    4. Lugar de Expedición (ej: "Bogotá D.C." si es visible)
    5. Huella digital (indicar "PRESENTE" o "AUSENTE")
    6. Firma (indicar "PRESENTE" o "AUSENTE")

    IMPORTANTE:
    - NO vuelvas a extraer nombres/apellidos (ya están en la frontal)
    - Si un campo no está visible, déjalo como string vacío ""
    - Responde en formato JSON válido
    - No agregues texto fuera del JSON

    Ejemplo:
    {"tipo_documento": "Cédula de Ciudadanía Vieja", "numero_documento": "12345678", "fecha_expedicion": "10/01/2020", "lugar_expedicion": "Bogotá D.C.", "huella_digital": "PRESENTE", "firma": "PRESENTE"}
    """,

    # ========== CÉDULA DE CIUDADANÍA NUEVA ==========
    # ========== NEW CITIZENSHIP CARD ==========
    "cedula_ciudadania_nueva_frontal": """
    Analiza esta CARA FRONTAL de una CÉDULA DE CIUDADANÍA COLOMBIANA (versión nueva, con diseño moderno, foto en el centro o derecha).
    Extrae SOLO la información visible en ESTA cara.

    NO extraigas datos que suelen estar en la cara trasera:
    - NO busques firma
    - NO busques huella digital
    - NO busques lugar de expedición

    Extrae:
    1. Tipo de Documento (ej: "Cédula de Ciudadanía Nueva")
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
    - Observa el diseño moderno de la cédula

    Ejemplo:
    {"tipo_documento": "Cédula de Ciudadanía Nueva", "numero_documento": "12345678", "nombres": "Juan Carlos", "apellidos": "Pérez López", "fecha_nacimiento": "15/03/1990", "sexo": "M", "nacionalidad": "Colombiana"}
    """,

    "cedula_ciudadania_nueva_trasera": """
    Analiza esta CARA TRASERA de una CÉDULA DE CIUDADANÍA COLOMBIANA (versión nueva).
    Extrae la información complementaria que aparece aquí.

    Extrae:
    1. Tipo de Documento (ej: "Cédula de Ciudadanía Nueva")
    2. Número de Documento (para verificar que coincida con frontal)
    3. Fecha de Expedición (si es visible)
    4. Lugar de Expedición (ej: "Bogotá D.C." si es visible)
    5. Huella digital (indicar "PRESENTE" o "AUSENTE")
    6. Firma (indicar "PRESENTE" o "AUSENTE")
    7. Datos biométricos adicionales (si hay alguno visible, como "CHIP" o "QR")

    IMPORTANTE:
    - NO vuelvas a extraer nombres/apellidos (ya están en la frontal)
    - Si un campo no está visible, déjalo como string vacío ""
    - Responde en formato JSON válido
    - No agregues texto fuera del JSON

    Ejemplo:
    {"tipo_documento": "Cédula de Ciudadanía Nueva", "numero_documento": "12345678", "fecha_expedicion": "10/01/2020", "lugar_expedicion": "Bogotá D.C.", "huella_digital": "PRESENTE", "firma": "PRESENTE", "datos_biometricos": "CHIP"}
    """,

    # ========== CÉDULA DIGITAL ==========
    # ========== DIGITAL CITIZENSHIP CARD ==========
    "cedula_digital_frontal": """
    Analiza esta CARA FRONTAL de una CÉDULA DIGITAL COLOMBIANA (con código QR y diseño moderno).
    Extrae SOLO la información visible en ESTA cara.

    NO extraigas datos que suelen estar en la cara trasera:
    - NO busques firma
    - NO busques huella digital
    - NO busques lugar de expedición

    Extrae:
    1. Tipo de Documento (ej: "Cédula Digital")
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
    - Identifica el código QR característico de la cédula digital

    Ejemplo:
    {"tipo_documento": "Cédula Digital", "numero_documento": "12345678", "nombres": "Juan Carlos", "apellidos": "Pérez López", "fecha_nacimiento": "15/03/1990", "sexo": "M", "nacionalidad": "Colombiana"}
    """,

    "cedula_digital_trasera": """
    Analiza esta CARA TRASERA de una CÉDULA DIGITAL COLOMBIANA.
    Extrae la información complementaria que aparece aquí.

    Extrae:
    1. Tipo de Documento (ej: "Cédula Digital")
    2. Número de Documento (para verificar que coincida con frontal)
    3. Fecha de Expedición (si es visible)
    4. Lugar de Expedición (ej: "Bogotá D.C." si es visible)
    5. Huella digital (indicar "PRESENTE" o "AUSENTE")
    6. Firma (indicar "PRESENTE" o "AUSENTE")
    7. Código QR (indicar "PRESENTE" o "AUSENTE")

    IMPORTANTE:
    - NO vuelvas a extraer nombres/apellidos (ya están en la frontal)
    - Si un campo no está visible, déjalo como string vacío ""
    - Responde en formato JSON válido
    - No agregues texto fuera del JSON

    Ejemplo:
    {"tipo_documento": "Cédula Digital", "numero_documento": "12345678", "fecha_expedicion": "10/01/2020", "lugar_expedicion": "Bogotá D.C.", "huella_digital": "PRESENTE", "firma": "PRESENTE", "codigo_qr": "PRESENTE"}
    """,

    # ========== TARJETA DE IDENTIDAD ==========
    # ========== IDENTITY CARD ==========
    "tarjeta_identidad_frontal": """
    Analiza esta CARA FRONTAL de una TARJETA DE IDENTIDAD COLOMBIANA (para menores de edad).
    Extrae SOLO la información visible en ESTA cara.

    NO extraigas datos que suelen estar en la cara trasera:
    - NO busques firma
    - NO busques huella digital
    - NO busques lugar de expedición

    Extrae:
    1. Tipo de Documento (ej: "Tarjeta de Identidad")
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
    - Observa que es para menores de edad

    Ejemplo:
    {"tipo_documento": "Tarjeta de Identidad", "numero_documento": "12345678", "nombres": "Juan Carlos", "apellidos": "Pérez López", "fecha_nacimiento": "15/03/2015", "sexo": "M", "nacionalidad": "Colombiana"}
    """,

    "tarjeta_identidad_trasera": """
    Analiza esta CARA TRASERA de una TARJETA DE IDENTIDAD COLOMBIANA.
    Extrae la información complementaria que aparece aquí.

    Extrae:
    1. Tipo de Documento (ej: "Tarjeta de Identidad")
    2. Número de Documento (para verificar que coincida con frontal)
    3. Fecha de Expedición (si es visible)
    4. Lugar de Expedición (ej: "Bogotá D.C." si es visible)
    5. Huella digital (indicar "PRESENTE" o "AUSENTE")
    6. Firma (indicar "PRESENTE" o "AUSENTE" - puede ser del menor o tutor)
    7. Grupo sanguíneo (si es visible)

    IMPORTANTE:
    - NO vuelvas a extraer nombres/apellidos (ya están en la frontal)
    - Si un campo no está visible, déjalo como string vacío ""
    - Responde en formato JSON válido
    - No agregues texto fuera del JSON

    Ejemplo:
    {"tipo_documento": "Tarjeta de Identidad", "numero_documento": "12345678", "fecha_expedicion": "10/01/2020", "lugar_expedicion": "Bogotá D.C.", "huella_digital": "AUSENTE", "firma": "PRESENTE", "grupo_sanguineo": "O+"}
    """,

    # ========== CÉDULA DE EXTRANJERÍA ==========
    # ========== FOREIGNER ID CARD ==========
    "cedula_extranjeria_frontal": """
    Analiza esta CARA FRONTAL de una CÉDULA DE EXTRANJERÍA COLOMBIANA.
    Extrae SOLO la información visible en ESTA cara.

    NO extraigas datos que suelen estar en la cara trasera:
    - NO busques firma
    - NO busques huella digital
    - NO busques lugar de expedición

    Extrae:
    1. Tipo de Documento (ej: "Cédula de Extranjería")
    2. Número de Documento (el número que aparece en esta cara)
    3. Nombres completos (si son visibles)
    4. Apellidos completos (si son visibles)
    5. Fecha de Nacimiento (si es visible)
    6. Sexo (M/F si es visible)
    7. Nacionalidad (si es visible - puede ser diferente de colombiana)

    IMPORTANTE:
    - Si un campo no está visible, déjalo como string vacío ""
    - Responde en formato JSON válido
    - No agregues texto fuera del JSON
    - Observa que es para extranjeros residentes en Colombia

    Ejemplo:
    {"tipo_documento": "Cédula de Extranjería", "numero_documento": "12345678", "nombres": "John Michael", "apellidos": "Smith Johnson", "fecha_nacimiento": "15/03/1985", "sexo": "M", "nacionalidad": "Estadounidense"}
    """,

    "cedula_extranjeria_trasera": """
    Analiza esta CARA TRASERA de una CÉDULA DE EXTRANJERÍA COLOMBIANA.
    Extrae la información complementaria que aparece aquí.

    Extrae:
    1. Tipo de Documento (ej: "Cédula de Extranjería")
    2. Número de Documento (para verificar que coincida con frontal)
    3. Fecha de Expedición (si es visible)
    4. Fecha de Vencimiento (si es visible - muy importante en cédulas de extranjería)
    5. Lugar de Expedición (ej: "Bogotá D.C." si es visible)
    6. Huella digital (indicar "PRESENTE" o "AUSENTE")
    7. Firma (indicar "PRESENTE" o "AUSENTE")
    8. Tipo de visa (si es visible, ej: "TP-4", "TP-11")

    IMPORTANTE:
    - NO vuelvas a extraer nombres/apellidos (ya están en la frontal)
    - Si un campo no está visible, déjalo como string vacío ""
    - Responde en formato JSON válido
    - No agregues texto fuera del JSON
    - La fecha de vencimiento es crítica en cédulas de extranjería

    Ejemplo:
    {"tipo_documento": "Cédula de Extranjería", "numero_documento": "12345678", "fecha_expedicion": "10/01/2020", "fecha_vencimiento": "10/01/2025", "lugar_expedicion": "Bogotá D.C.", "huella_digital": "PRESENTE", "firma": "PRESENTE", "tipo_visa": "TP-4"}
    """,

    # ========== PASAPORTE COLOMBIANO ==========
    # ========== COLOMBIAN PASSPORT ==========
    "pasaporte_completo": """
    Analiza este PASAPORTE COLOMBIANO.
    Extrae TODA la información visible en esta única cara.

    Extrae:
    1. Tipo de Documento (ej: "Pasaporte")
    2. Número de Pasaporte (ej: "AB1234567")
    3. Nombres completos
    4. Apellidos completos
    5. Fecha de Nacimiento
    6. Sexo (M/F)
    7. Nacionalidad
    8. Fecha de Expedición
    9. Fecha de Vencimiento (muy importante para pasaportes)
    10. Lugar de Nacimiento (si es visible)

    IMPORTANTE:
    - Si un campo no está visible, déjalo como string vacío ""
    - Responde en formato JSON válido
    - No agregues texto fuera del JSON
    - Observa las líneas legibles en formato máquina (MRZ) al final si existen

    Ejemplo:
    {"tipo_documento": "Pasaporte", "numero_documento": "AB1234567", "nombres": "Juan Carlos", "apellidos": "Pérez López", "fecha_nacimiento": "15/03/1990", "sexo": "M", "nacionalidad": "Colombiana", "fecha_expedicion": "01/01/2020", "fecha_vencimiento": "01/01/2030", "lugar_nacimiento": "Bogotá, Colombia"}
    """,

    # ========== PERMISO PPT ==========
    # ========== PPT PERMIT ==========
    "ppt_completo": """
    Analiza este PERMISO PPT (Permiso por Protección Temporal) COLOMBIANO.
    Extrae TODA la información visible en esta única cara.

    Extrae:
    1. Tipo de Documento (ej: "Permiso PPT")
    2. Número de PPT (el número de documento)
    3. Nombres completos
    4. Apellidos completos
    5. Fecha de Nacimiento (si es visible)
    6. Sexo (M/F si es visible)
    7. Nacionalidad (si es visible)
    8. Fecha de Expedición (si es visible)
    9. Fecha de Vencimiento (si es visible - muy importante en PPT)
    10. Lugar de Expedición (si es visible)

    IMPORTANTE:
    - Si un campo no está visible, déjalo como string vacío ""
    - Responde en formato JSON válido
    - No agregues texto fuera del JSON
    - El PPT es un documento temporal para migrantes

    Ejemplo:
    {"tipo_documento": "Permiso PPT", "numero_documento": "12345678", "nombres": "Juan Carlos", "apellidos": "Pérez López", "fecha_nacimiento": "15/03/1990", "sexo": "M", "nacionalidad": "Venezolana", "fecha_expedicion": "10/01/2024", "fecha_vencimiento": "10/01/2025", "lugar_expedicion": "Bogotá D.C."}
    """,

    # ========== OTROS DOCUMENTOS (GENÉRICO) ==========
    # ========== OTHER DOCUMENTS (GENERIC) ==========
    "otro_completo": """
    Analiza este DOCUMENTO COLOMBIANO.
    Extrae TODA la información visible que puedas identificar.

    Extrae:
    1. Tipo de Documento (identifica qué tipo es, ej: "Licencia de Conducción", "Registro Civil", etc.)
    2. Número de Documento (si es visible)
    3. Nombres completos (si son visibles)
    4. Apellidos completos (si son visibles)
    5. Fecha de Nacimiento (si es visible)
    6. Sexo (M/F si es visible)
    7. Nacionalidad (si es visible)

    IMPORTANTE:
    - Si un campo no está visible, déjalo como string vacío ""
    - Responde en formato JSON válido
    - No agregues texto fuera del JSON
    - Identifica el tipo específico de documento

    Ejemplo:
    {"tipo_documento": "Licencia de Conducción", "numero_documento": "12345678", "nombres": "Juan Carlos", "apellidos": "Pérez López", "fecha_nacimiento": "15/03/1990", "sexo": "M", "nacionalidad": "Colombiana"}
    """,

    # ========== PROMPT PARA CLASIFICACIÓN DE CARA ==========
    # ========== PROMPT FOR FACE CLASSIFICATION ==========
    "clasificar_cara": """
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
    """,

    # ========== PROMPT PARA DETECTAR CARAS MIXTAS ==========
    # ========== PROMPT FOR DETECTING MIXED FACES ==========
    "detectar_mixto": """
    Analiza esta imagen y determina si contiene DOS caras de un documento colombiano.

    Busca:
    - Dos secciones claramente divididas (una arriba, otra abajo)
    - Elementos de AMBOS: foto Y firma/huella
    - Dos números de documento diferentes
    - Texto que se repite o que indica dos lados
    - Dos encabezados o títulos de documento

    Responde SOLO con "SI" o "NO".
    """,

    # ========== PROMPT PARA COORDENADAS DE DIVISIÓN ==========
    # ========== PROMPT FOR SPLIT COORDINATES ==========
    "coordenadas_division": """
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
}


def get_prompt(document_type: str, face_type: str) -> str:
    """
    Obtiene el prompt específico para un tipo de documento y tipo de cara.

    Args:
        document_type: Tipo de documento (ej: "cedula_ciudadania_vieja", "pasaporte", etc.)
        face_type: Tipo de cara ("frontal", "trasera", "completo")

    Returns:
        El prompt específico o un prompt genérico si no existe

    Gets the specific prompt for a document type and face type.

    Args:
        document_type: Document type (e.g.: "cedula_ciudadania_vieja", "pasaporte", etc.)
        face_type: Face type ("frontal", "trasera", "completo")

    Returns:
        The specific prompt or a generic prompt if not found
    """
    prompt_key = f"{document_type}_{face_type}"
    return DOCUMENT_PROMPTS.get(prompt_key, DOCUMENT_PROMPTS["otro_completo"])


def get_classification_prompt() -> str:
    """Obtiene el prompt para clasificar una cara.
    Gets the prompt for classifying a face."""
    return DOCUMENT_PROMPTS["clasificar_cara"]


def get_mixed_detection_prompt() -> str:
    """Obtiene el prompt para detectar caras mixtas.
    Gets the prompt for detecting mixed faces."""
    return DOCUMENT_PROMPTS["detectar_mixto"]


def get_split_coordinates_prompt() -> str:
    """Obtiene el prompt para obtener coordenadas de división.
    Gets the prompt for obtaining split coordinates."""
    return DOCUMENT_PROMPTS["coordenadas_division"]


def get_retry_prompt(existing_data: Dict[str, str], missing_fields: List[str]) -> str:
    """
    Genera un prompt de re-intento enfocado solo en los campos faltantes.

    Generates a retry prompt focused only on the missing fields.
    """
    campos_encontrados = []
    for key, value in existing_data.items():
        if value and value.strip():
            campos_encontrados.append(f"  - {key}: {value}")

    campos_str = "\n".join(campos_encontrados) if campos_encontrados else "  (ninguno)"
    faltantes_str = ", ".join(missing_fields)

    return f"""Ya analizamos esta imagen de un documento colombiano y obtuvimos datos parciales.

CAMPOS YA EXTRAIDOS CORRECTAMENTE:
{campos_str}

CAMPOS FALTANTES QUE NECESITAMOS: {faltantes_str}

Concentrate SOLAMENTE en encontrar los campos faltantes.
Lee el texto con MUCHO cuidado, caracter por caracter.
Busca en toda la imagen, incluyendo textos pequenos o borrosos.

Responde SOLO con JSON conteniendo UNICAMENTE los campos faltantes:
{{"campo_faltante_1": "valor", "campo_faltante_2": "valor"}}

Si un campo simplemente no es visible, dejalo como string vacio ""."""


def get_all_document_types() -> list:
    """Retorna la lista de todos los tipos de documentos soportados.
    Returns the list of all supported document types."""
    return [
        "cedula_ciudadania_vieja",
        "cedula_ciudadania_nueva",
        "cedula_digital",
        "tarjeta_identidad",
        "cedula_extranjeria",
        "pasaporte",
        "ppt",
        "otro"
    ]


def get_two_face_document_types() -> list:
    """Retorna la lista de tipos de documentos que tienen 2 caras.
    Returns the list of document types that have 2 faces."""
    return [
        "cedula_ciudadania_vieja",
        "cedula_ciudadania_nueva",
        "cedula_digital",
        "tarjeta_identidad",
        "cedula_extranjeria"
    ]


def get_one_face_document_types() -> list:
    """Retorna la lista de tipos de documentos que tienen 1 sola cara.
    Returns the list of document types that have only 1 face."""
    return [
        "pasaporte",
        "ppt",
        "otro"
    ]
