"""
Procesador por lotes con pipeline concurrente.
Combina clasificación + extracción en una sola llamada a Gemini.
Procesa múltiples páginas en paralelo con control de concurrencia.

Batch processor with concurrent pipeline.
Combines classification + extraction in a single Gemini call.
Processes multiple pages in parallel with concurrency control.
"""

import os

import json
import asyncio
import hashlib
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from dotenv import load_dotenv
from PIL import Image
from google import genai
from google.genai import types

from services.data_merger import merge_face_data, merge_one_face_data, clean_merged_data
from services.mixed_face_detector import is_likely_mixed_heuristic
from services.data_validator import validate_extracted_data
from services.document_prompts import get_retry_prompt

load_dotenv()

logger = logging.getLogger(__name__)

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Unified prompt that classifies + extracts in a SINGLE call (Spanish prompt for Colombian ID documents)
# Prompt unificado que clasifica + extrae en UNA SOLA llamada
UNIFIED_PROMPT = """Eres un experto en documentos de identidad colombianos. Analiza con mucho cuidado esta imagen escaneada.

PASO 1 — CLASIFICACIÓN:
Determina qué ves en la imagen:
- face_type:
  * "FRONTAL": La cara principal del documento. Contiene la FOTO de la persona, los NOMBRES, APELLIDOS, NÚMERO de documento, FECHA DE NACIMIENTO.
  * "TRASERA": La cara posterior del documento. Contiene FIRMA, HUELLA DIGITAL, FECHA DE EXPEDICIÓN, LUGAR DE EXPEDICIÓN. NO suele tener foto.
  * "COMPLETO": Toda la información está en una sola cara (pasaportes, contraseñas, PPT).
  * "MIXTO": La imagen contiene AMBAS caras (frontal y trasera) en una sola imagen, generalmente una arriba y otra abajo.

- document_type: Identifica el tipo exacto de documento colombiano:
  * "cedula_ciudadania_vieja": Cédula antigua, amarilla/rosada, diseño viejo
  * "cedula_ciudadania_nueva": Cédula con diseño moderno, hologramas
  * "cedula_digital": Cédula Digital con código QR prominente
  * "tarjeta_identidad": Tarjeta de Identidad para menores de edad (azul)
  * "cedula_extranjeria": Cédula de Extranjería para extranjeros
  * "pasaporte": Pasaporte colombiano
  * "ppt": Permiso por Protección Temporal (PPT)
  * "contraseña": Contraseña provisional (documento temporal de papel)
  * "otro": Cualquier otro documento no identificable

PASO 2 — EXTRACCIÓN:
Extrae ABSOLUTAMENTE TODOS los datos visibles. Lee con mucho cuidado cada texto en la imagen.

INSTRUCCIONES ESPECÍFICAS:
- NÚMERO DE DOCUMENTO: Busca el número largo (6-12 dígitos). En cédulas aparece después de "No." o "C.C." o "NUIP". Copia TODOS los dígitos completos, incluyendo puntos si los tiene.
- NOMBRES: Los nombres de pila (ej: "JUAN CARLOS", "MARIA FERNANDA"). Busca después de "NOMBRES" en el documento.
- APELLIDOS: Los apellidos completos (ej: "PÉREZ LÓPEZ", "GARCÍA MARTÍNEZ"). Busca después de "APELLIDOS" en el documento.
- FECHA DE NACIMIENTO: Formato DD/MM/YYYY con el año COMPLETO de 4 dígitos (ej: "15/03/1990", NO "15/03/199").
- SEXO: "M" para masculino, "F" para femenino.
- NACIONALIDAD: Para documentos colombianos SIEMPRE pon "COLOMBIANA". Solo pon algo diferente si el documento explícitamente dice otra nacionalidad (ej: cédula de extranjería puede tener otra).
- TIPO DE DOCUMENTO: Usa nombre legible: "Cédula de Ciudadanía", "Cédula Digital", "Tarjeta de Identidad", "Cédula de Extranjería", "Pasaporte", "Permiso PPT", "Contraseña".

PARA CARAS TRASERAS:
- Aún así extrae el NÚMERO DE DOCUMENTO si es visible (suele repetirse en el reverso).
- Extrae FECHA DE EXPEDICIÓN, LUGAR DE EXPEDICIÓN.
- Indica FIRMA: "PRESENTE" o "AUSENTE".
- Indica HUELLA DIGITAL: "PRESENTE" o "AUSENTE".

Responde SOLO con este JSON exacto (sin texto adicional, sin explicaciones):
{
    "classification": {
        "face_type": "...",
        "document_type": "...",
        "confidence": 0.95
    },
    "data": {
        "tipo_documento": "...",
        "numero_documento": "...",
        "nombres": "...",
        "apellidos": "...",
        "fecha_nacimiento": "DD/MM/YYYY",
        "sexo": "M o F",
        "nacionalidad": "COLOMBIANA",
        "fecha_expedicion": "",
        "fecha_vencimiento": "",
        "lugar_expedicion": "",
        "lugar_nacimiento": "",
        "huella_digital": "",
        "firma": "",
        "codigo_qr": "",
        "grupo_sanguineo": ""
    }
}

REGLAS ESTRICTAS:
1. Si un campo NO es visible en esta cara, déjalo como string vacío ""
2. Las fechas SIEMPRE con año de 4 dígitos: DD/MM/YYYY (ej: "15/03/1990")
3. Nacionalidad por defecto "COLOMBIANA" para cédulas, tarjetas de identidad y contraseñas
4. Lee el texto MUY CUIDADOSAMENTE, carácter por carácter
5. NO inventes datos que no puedas leer claramente en la imagen
"""

# Campos requeridos para considerar un documento "completo"
# Required fields to consider a document "complete"
REQUIRED_DATA_FIELDS = ["numero_documento", "nombres", "apellidos"]

# Configuracion de reintentos
# Retry configuration
MAX_RETRIES = 2
RETRY_BASE_DELAY = 2.0


@dataclass
class PageResult:
    """Resultado del procesamiento de una página.
    Result of processing a single page."""
    page_number: int
    face_type: str = "DESCONOCIDO"
    document_type: str = "otro"
    confidence: float = 0.0
    data: Dict[str, str] = field(default_factory=dict)
    is_mixed: bool = False
    error: Optional[str] = None
    missing_fields: List[str] = field(default_factory=list)


@dataclass
class ProcessingProgress:
    """Estado del progreso de procesamiento.
    Processing progress state."""
    total_pages: int = 0
    processed_pages: int = 0
    current_page: int = 0
    documents_found: int = 0
    errors: int = 0
    status: str = "idle"  # idle, processing, done, error

    @property
    def percentage(self) -> float:
        """Porcentaje de progreso calculado.
        Calculated progress percentage."""
        if self.total_pages == 0:
            return 0.0
        return (self.processed_pages / self.total_pages) * 100


# Caché global de resultados por hash de imagen
# Global cache of results by image hash
_result_cache: Dict[str, PageResult] = {}


def _get_image_hash(image_bytes: bytes) -> str:
    """Genera un hash MD5 de la imagen para caché.
    Generates an MD5 hash of the image for caching."""
    return hashlib.md5(image_bytes).hexdigest()


def _parse_unified_response(response_text: str) -> Dict:
    """Parsea la respuesta del prompt unificado.
    Parses the response from the unified prompt."""
    try:
        response_text = response_text.strip()

        if response_text.startswith("```json"):
            response_text = response_text[7:]
        elif response_text.startswith("```"):
            response_text = response_text[3:]

        if response_text.endswith("```"):
            response_text = response_text[:-3]

        response_text = response_text.strip()
        return json.loads(response_text)

    except json.JSONDecodeError as e:
        logger.error(f"Error al parsear respuesta unificada: {e}")
        return {}


async def process_single_page(
    client: genai.Client,
    image_bytes: bytes,
    page_number: int,
    semaphore: asyncio.Semaphore,
    progress: Optional[ProcessingProgress] = None
) -> PageResult:
    """
    Procesa UNA pagina con el prompt unificado (clasificar + extraer en 1 llamada).
    Incluye retry con backoff exponencial y re-procesamiento selectivo.

    Processes ONE page with the unified prompt (classify + extract in 1 call).
    Includes retry with exponential backoff and selective re-processing.
    """
    # Verificar cache
    # Check cache
    img_hash = _get_image_hash(image_bytes)
    if img_hash in _result_cache:
        logger.debug(f"Cache hit para pagina {page_number + 1}")
        cached = _result_cache[img_hash]
        if progress:
            progress.processed_pages += 1
        return cached

    async with semaphore:
        if progress:
            progress.current_page = page_number + 1

        logger.info(f"Procesando pagina {page_number + 1}...")

        last_error = None

        for attempt in range(MAX_RETRIES + 1):
            try:
                if attempt > 0:
                    delay = RETRY_BASE_DELAY * (2 ** (attempt - 1))
                    logger.warning(
                        f"Reintento {attempt}/{MAX_RETRIES} para pagina {page_number + 1} "
                        f"(espera {delay}s)"
                    )
                    await asyncio.sleep(delay)

                def _call_gemini():
                    return client.models.generate_content(
                        model=GEMINI_MODEL,
                        contents=[
                            types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                            UNIFIED_PROMPT
                        ]
                    )

                response = await asyncio.to_thread(_call_gemini)

                parsed = _parse_unified_response(response.text)

                if not parsed:
                    last_error = "No se pudo parsear la respuesta"
                    if attempt == MAX_RETRIES:
                        result = PageResult(page_number=page_number, error=last_error)
                        if progress:
                            progress.errors += 1
                            progress.processed_pages += 1
                        return result
                    continue

                classification = parsed.get("classification", {})
                data = parsed.get("data", {})

                # Asegurar campos requeridos
                # Ensure required fields exist
                for field_name in ["tipo_documento", "numero_documento", "nombres",
                                   "apellidos", "fecha_nacimiento", "sexo", "nacionalidad",
                                   "fecha_expedicion", "fecha_vencimiento", "lugar_expedicion",
                                   "lugar_nacimiento", "huella_digital", "firma", "codigo_qr",
                                   "datos_biometricos", "grupo_sanguineo", "tipo_visa"]:
                    if field_name not in data:
                        data[field_name] = ""

                face_type = classification.get("face_type", "DESCONOCIDO")
                confidence = classification.get("confidence", 0.0)

                # Validar datos extraidos
                # Validate extracted data
                validation = validate_extracted_data(data, face_type, confidence)
                data = validation.cleaned_data

                if validation.warnings:
                    logger.debug(
                        f"Validacion pagina {page_number + 1}: "
                        f"{len(validation.warnings)} warnings"
                    )

                result = PageResult(
                    page_number=page_number,
                    face_type=face_type,
                    document_type=classification.get("document_type", "otro"),
                    confidence=confidence,
                    data=data,
                    is_mixed=face_type == "MIXTO"
                )

                # Detectar campos faltantes
                # Detect missing fields
                if result.face_type in ["FRONTAL", "COMPLETO", "MIXTO"]:
                    for req_field in REQUIRED_DATA_FIELDS:
                        if not data.get(req_field, "").strip():
                            result.missing_fields.append(req_field)

                # Re-procesamiento selectivo si faltan campos criticos
                # Selective re-processing if critical fields are missing
                if result.missing_fields:
                    result = await _retry_missing_fields(
                        client, image_bytes, page_number, result
                    )

                # Guardar en cache
                # Save to cache
                _result_cache[img_hash] = result

                if progress:
                    progress.processed_pages += 1

                status_icon = "✅" if not result.missing_fields else "⚠️"
                logger.info(
                    f"{status_icon} Pagina {page_number + 1}: {result.face_type} - "
                    f"{result.document_type} ({result.confidence:.0%})"
                    + (f" [Faltan: {', '.join(result.missing_fields)}]" if result.missing_fields else "")
                )

                return result

            except Exception as e:
                last_error = str(e)
                logger.warning(
                    f"Error en pagina {page_number + 1} (intento {attempt + 1}/{MAX_RETRIES + 1}): {e}"
                )
                if attempt == MAX_RETRIES:
                    logger.error(f"❌ Pagina {page_number + 1} fallo despues de {MAX_RETRIES + 1} intentos")
                    if progress:
                        progress.errors += 1
                        progress.processed_pages += 1
                    return PageResult(page_number=page_number, error=last_error)

        # No deberia llegar aqui, pero por seguridad
        # Should not reach here, but as a safety measure
        if progress:
            progress.errors += 1
            progress.processed_pages += 1
        return PageResult(page_number=page_number, error=last_error or "Error desconocido")


async def _retry_missing_fields(
    client: genai.Client,
    image_bytes: bytes,
    page_number: int,
    result: PageResult
) -> PageResult:
    """
    Re-procesa una pagina para intentar obtener campos faltantes criticos.
    Solo hace 1 intento adicional con un prompt enfocado.

    Re-processes a page to try to obtain missing critical fields.
    Only makes 1 additional attempt with a focused prompt.
    """
    missing = result.missing_fields
    if not missing:
        return result

    # Solo re-procesar si faltan campos criticos
    # Only re-process if critical fields are missing
    critical_missing = [f for f in missing if f in REQUIRED_DATA_FIELDS]
    if not critical_missing:
        return result

    try:
        logger.info(
            f"Re-procesando pagina {page_number + 1} para campos faltantes: "
            f"{', '.join(critical_missing)}"
        )

        retry_prompt = get_retry_prompt(result.data, critical_missing)

        def _call_gemini_retry():
            return client.models.generate_content(
                model=GEMINI_MODEL,
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                    retry_prompt
                ]
            )

        response = await asyncio.to_thread(_call_gemini_retry)
        parsed = _parse_unified_response(response.text)

        if not parsed:
            logger.debug(f"Re-intento no devolvio JSON valido para pagina {page_number + 1}")
            return result

        # Combinar: mantener datos originales, agregar los nuevos
        # Combine: keep original data, add the new ones
        recovered = []
        for field in critical_missing:
            new_value = parsed.get(field, "").strip()
            if new_value:
                result.data[field] = new_value
                recovered.append(field)

        if recovered:
            # Actualizar missing_fields
            # Update missing_fields
            result.missing_fields = [f for f in result.missing_fields if f not in recovered]
            logger.info(
                f"✅ Pagina {page_number + 1}: recuperados {', '.join(recovered)} "
                f"en re-intento"
            )
        else:
            logger.debug(f"Re-intento no recupero campos para pagina {page_number + 1}")

    except Exception as e:
        logger.warning(f"Error en re-procesamiento de pagina {page_number + 1}: {e}")

    return result


async def process_pages_batch(
    images: List[bytes],
    max_concurrent: int = 5,
    progress: Optional[ProcessingProgress] = None
) -> List[PageResult]:
    """
    Procesa todas las páginas en paralelo con control de concurrencia.

    Args:
        images: Lista de imágenes de páginas
        max_concurrent: Máximo de llamadas concurrentes a Gemini
        progress: Objeto de progreso para tracking

    Returns:
        Lista de PageResult con los datos de cada página

    Processes all pages in parallel with concurrency control.

    Args:
        images: List of page images
        max_concurrent: Maximum concurrent calls to Gemini
        progress: Progress object for tracking

    Returns:
        List of PageResult with data for each page
    """
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        raise ValueError("API key de Gemini no configurada. Agrega GEMINI_API_KEY al archivo .env")

    client = genai.Client(api_key=api_key)
    semaphore = asyncio.Semaphore(max_concurrent)

    if progress:
        progress.total_pages = len(images)
        progress.status = "processing"

    # Procesamos todas las páginas concurrentemente (limitadas por semáforo)
    # Process all pages concurrently (limited by semaphore)
    tasks = [
        process_single_page(client, img, i, semaphore, progress)
        for i, img in enumerate(images)
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Manejar excepciones que escaparon
    # Handle exceptions that escaped
    processed_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"Excepción no manejada en página {i + 1}: {result}")
            processed_results.append(PageResult(page_number=i, error=str(result)))
        else:
            processed_results.append(result)

    if progress:
        progress.status = "done"

    return processed_results


def group_pages_into_documents(results: List[PageResult]) -> List[Dict[str, str]]:
    """
    Agrupa los resultados de páginas en documentos lógicos.
    Empareja caras frontales con traseras consecutivas del mismo tipo.

    Args:
        results: Lista de PageResult ordenados por número de página

    Returns:
        Lista de diccionarios con datos combinados de documentos

    Groups page results into logical documents.
    Pairs front faces with consecutive back faces of the same type.

    Args:
        results: List of PageResult sorted by page number

    Returns:
        List of dictionaries with combined document data
    """
    # Ordenar por número de página
    # Sort by page number
    sorted_results = sorted(results, key=lambda r: r.page_number)

    merged_documents = []
    pending_frontal: Optional[PageResult] = None

    two_face_types = [
        "cedula_ciudadania_vieja", "cedula_ciudadania_nueva",
        "cedula_digital", "tarjeta_identidad", "cedula_extranjeria"
    ]

    for result in sorted_results:
        if result.error:
            # Página con error, la saltamos
            # Page with error, skip it
            logger.warning(f"Página {result.page_number + 1} con error, saltando")
            continue

        if result.face_type == "FRONTAL":
            # Si teníamos una frontal pendiente, la guardamos como 1 cara
            # If we had a pending front face, save it as 1 face
            if pending_frontal:
                merged = merge_one_face_data(pending_frontal.data, pending_frontal.document_type)
                merged = clean_merged_data(merged)
                merged_documents.append(merged)

            # Esta es la nueva frontal pendiente
            # This is the new pending front face
            pending_frontal = result

        elif result.face_type == "TRASERA":
            # Intentamos emparejar con la frontal pendiente
            # Try to pair with the pending front face
            if (pending_frontal and
                pending_frontal.document_type == result.document_type and
                pending_frontal.document_type in two_face_types):
                # Emparejamos frontal + trasera
                # Pair front + back
                merged = merge_face_data(
                    pending_frontal.data, result.data,
                    pending_frontal.document_type
                )
                merged = clean_merged_data(merged)
                merged_documents.append(merged)
                pending_frontal = None
            else:
                # No hay frontal compatible, guardamos la trasera sola
                # No compatible front face, save the back face alone
                if pending_frontal:
                    merged = merge_one_face_data(pending_frontal.data, pending_frontal.document_type)
                    merged = clean_merged_data(merged)
                    merged_documents.append(merged)
                    pending_frontal = None

                merged = merge_one_face_data(result.data, result.document_type)
                merged = clean_merged_data(merged)
                merged_documents.append(merged)

        elif result.face_type in ["COMPLETO", "DESCONOCIDO"]:
            # Guardamos la frontal pendiente si existe
            # Save the pending front face if it exists
            if pending_frontal:
                merged = merge_one_face_data(pending_frontal.data, pending_frontal.document_type)
                merged = clean_merged_data(merged)
                merged_documents.append(merged)
                pending_frontal = None

            # Documento de 1 cara
            # Single-face document
            merged = merge_one_face_data(result.data, result.document_type)
            merged = clean_merged_data(merged)
            merged_documents.append(merged)

        elif result.face_type == "MIXTO":
            # Guardamos la frontal pendiente si existe
            # Save the pending front face if it exists
            if pending_frontal:
                merged = merge_one_face_data(pending_frontal.data, pending_frontal.document_type)
                merged = clean_merged_data(merged)
                merged_documents.append(merged)
                pending_frontal = None

            # Para mixto, ya tenemos los datos de la llamada unificada
            # For mixed, we already have the data from the unified call
            merged = merge_one_face_data(result.data, result.document_type)
            merged = clean_merged_data(merged)
            merged_documents.append(merged)

    # Si quedó una frontal pendiente al final
    # If a front face remained pending at the end
    if pending_frontal:
        merged = merge_one_face_data(pending_frontal.data, pending_frontal.document_type)
        merged = clean_merged_data(merged)
        merged_documents.append(merged)

    return merged_documents


def generate_problem_report(results: List[PageResult]) -> List[Dict[str, str]]:
    """
    Genera un reporte de páginas con problemas para incluir en el Excel.

    Args:
        results: Lista de PageResult

    Returns:
        Lista de diccionarios con info de cada página problemática

    Generates a report of pages with problems to include in the Excel.

    Args:
        results: List of PageResult

    Returns:
        List of dictionaries with info for each problematic page
    """
    problems = []
    field_names_es = {
        "numero_documento": "Número de Documento",
        "nombres": "Nombres",
        "apellidos": "Apellidos",
        "fecha_nacimiento": "Fecha de Nacimiento",
        "sexo": "Sexo",
        "nacionalidad": "Nacionalidad"
    }

    for result in sorted(results, key=lambda r: r.page_number):
        page_num = result.page_number + 1  # 1-indexed para el usuario
        # 1-indexed para el usuario
        # 1-indexed for the user

        if result.error:
            problems.append({
                "Página": str(page_num),
                "Estado": "❌ ERROR",
                "Tipo de Cara": result.face_type,
                "Tipo de Documento": result.document_type,
                "Problema": f"Error al procesar: {result.error}",
                "Acción Sugerida": "Revise esta página manualmente y digite los datos"
            })
        elif result.missing_fields:
            campos_faltantes = [field_names_es.get(f, f) for f in result.missing_fields]
            problems.append({
                "Página": str(page_num),
                "Estado": "⚠️ INCOMPLETO",
                "Tipo de Cara": result.face_type,
                "Tipo de Documento": result.data.get("tipo_documento", result.document_type),
                "Problema": f"Campos faltantes: {', '.join(campos_faltantes)}",
                "Acción Sugerida": "Verifique los datos de esta página y complete manualmente"
            })
        elif result.face_type == "DESCONOCIDO":
            problems.append({
                "Página": str(page_num),
                "Estado": "⚠️ NO IDENTIFICADO",
                "Tipo de Cara": "DESCONOCIDO",
                "Tipo de Documento": result.data.get("tipo_documento", ""),
                "Problema": "No se pudo identificar el tipo de cara del documento",
                "Acción Sugerida": "Revise esta página manualmente"
            })

    return problems


def clear_cache():
    """Limpia el caché de resultados.
    Clears the results cache."""
    global _result_cache
    _result_cache.clear()
    logger.info("Caché de resultados limpiado")
