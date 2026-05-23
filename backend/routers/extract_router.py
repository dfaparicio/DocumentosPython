"""
Router que define el endpoint para procesar PDFs de documentos colombianos.
Usa procesamiento concurrente por lotes para máxima velocidad.

Router that defines the endpoint for processing Colombian document PDFs.
Uses concurrent batch processing for maximum speed.
"""

import asyncio
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse

from services.pdf_service import convert_pdf_to_images
from services.excel_service import create_excel_with_merged_documents
from services.batch_processor import (
    process_pages_batch,
    group_pages_into_documents,
    generate_problem_report,
    ProcessingProgress,
    clear_cache
)

logger = logging.getLogger(__name__)

# Creamos el router
# We create the router
router = APIRouter(prefix="/extract", tags=["extracción"])

# Progreso global para WebSocket
# Global progress for WebSocket
_current_progress: ProcessingProgress = ProcessingProgress()


def _enrich_documents_with_page_info(documents, page_results):
    """Agrega info de pagina origen y confianza a cada documento.

    Adds source page info and confidence to each document.
    """
    def _confidence_label(confidence):
        if confidence >= 0.9:
            return "Alta"
        elif confidence >= 0.7:
            return "Media"
        elif confidence >= 0.5:
            return "Baja"
        return "Muy Baja"

    # Mapear paginas a sus resultados
    # Map pages to their results
    page_by_number = {}
    for pr in page_results:
        if not pr.error:
            page_by_number[pr.page_number] = pr

    # Para cada documento, buscar la pagina que lo origino
    # Como group_pages_into_documents procesa secuencialmente,
    # usamos el tipo y cara para hacer la correspondencia
    # For each document, find the page that originated it
    # Since group_pages_into_documents processes sequentially,
    # we use the type and face to make the correspondence
    doc_idx = 0
    for pr in sorted(page_results, key=lambda r: r.page_number):
        if pr.error:
            continue
        if pr.face_type in ("FRONTAL", "COMPLETO", "MIXTO"):
            if doc_idx < len(documents):
                documents[doc_idx]["_page_origin"] = str(pr.page_number + 1)
                documents[doc_idx]["_confidence_label"] = _confidence_label(pr.confidence)
                doc_idx += 1


@router.post("/")
async def extract_from_pdf(pdf_file: UploadFile = File(...)):
    """
    Endpoint principal: recibe un PDF de documentos colombianos y devuelve un Excel.

    Pipeline optimizado:
    1. PDF → imágenes JPEG (100 DPI)
    2. Clasificación + Extracción en UNA llamada por página (concurrente)
    3. Agrupación de páginas en documentos lógicos
    4. Generación de Excel

    Args:
        pdf_file: El archivo PDF enviado por el usuario

    Returns:
        Un archivo Excel para descargar con los datos de todos los documentos

    Main endpoint: receives a PDF of Colombian documents and returns an Excel file.

    Optimized pipeline:
    1. PDF → JPEG images (100 DPI)
    2. Classification + Extraction in ONE call per page (concurrent)
    3. Grouping of pages into logical documents
    4. Excel generation

    Args:
        pdf_file: The PDF file sent by the user

    Returns:
        An Excel file to download with the data of all documents
    """
    global _current_progress

    # Verificamos que el archivo sea un PDF
    # We verify that the file is a PDF
    if not pdf_file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="El archivo debe ser un PDF"
        )

    try:
        # PASO 1: Leemos el PDF y lo convertimos a imágenes JPEG
        # STEP 1: We read the PDF and convert it to JPEG images
        _current_progress = ProcessingProgress(status="converting")
        pdf_bytes = await pdf_file.read()
        images_list = convert_pdf_to_images(pdf_bytes)

        if not images_list:
            raise HTTPException(
                status_code=400,
                detail="No se pudo procesar el PDF. Asegúrate de que el archivo es válido."
            )

        logger.info(f"PDF convertido a {len(images_list)} imágenes JPEG")

        # PASO 2: Procesamiento concurrente — clasificar + extraer en 1 llamada por página
        # STEP 2: Concurrent processing — classify + extract in 1 call per page
        _current_progress = ProcessingProgress(
            total_pages=len(images_list),
            status="processing"
        )

        page_results = await process_pages_batch(
            images=images_list,
            max_concurrent=5,  # 5 llamadas concurrentes a Gemini
            # 5 concurrent calls to Gemini
            progress=_current_progress
        )

        # Contar errores
        # Count errors
        errors = sum(1 for r in page_results if r.error)
        successful = len(page_results) - errors
        logger.info(f"Procesadas {successful}/{len(page_results)} páginas ({errors} errores)")

        # PASO 3: Agrupamos las páginas en documentos lógicos
        # STEP 3: We group the pages into logical documents
        merged_data_list = group_pages_into_documents(page_results)

        if not merged_data_list:
            raise HTTPException(
                status_code=400,
                detail="No se pudo extraer ningún dato de los documentos."
            )

        _current_progress.documents_found = len(merged_data_list)
        logger.info(f"Se encontraron {len(merged_data_list)} documentos")

        # Enriquecer documentos con info de pagina y confianza
        # Enrich documents with page info and confidence
        _enrich_documents_with_page_info(merged_data_list, page_results)

        # PASO 4: Generamos reporte de páginas con problemas
        # STEP 4: We generate a report of pages with problems
        problem_report = generate_problem_report(page_results)
        if problem_report:
            logger.info(f"⚠️ {len(problem_report)} páginas requieren revisión manual")

        # PASO 5: Creamos el Excel con datos + reporte de problemas
        # STEP 5: We create the Excel with data + problem report
        excel_buffer = create_excel_with_merged_documents(
            merged_data_list, problem_report, page_results
        )

        _current_progress.status = "done"

        # PASO 5: Devolvemos el Excel al usuario
        # STEP 5: We return the Excel to the user
        return StreamingResponse(
            excel_buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": "attachment; filename=documentos_extraidos.xlsx"
            }
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        _current_progress.status = "error"
        raise HTTPException(
            status_code=500,
            detail="Ocurrió un error al procesar el archivo. Por favor intenta de nuevo."
        )


@router.get("/progress")
async def get_progress():
    """
    Endpoint para consultar el progreso del procesamiento actual.

    Returns:
        Estado actual del procesamiento con porcentaje

    Endpoint to query the progress of the current processing.

    Returns:
        Current processing status with percentage
    """
    return {
        "status": _current_progress.status,
        "total_pages": _current_progress.total_pages,
        "processed_pages": _current_progress.processed_pages,
        "current_page": _current_progress.current_page,
        "documents_found": _current_progress.documents_found,
        "errors": _current_progress.errors,
        "percentage": round(_current_progress.percentage, 1)
    }


@router.websocket("/ws/progress")
async def websocket_progress(websocket: WebSocket):
    """
    WebSocket para progreso en tiempo real.
    El frontend puede conectarse aquí para ver el avance.

    WebSocket for real-time progress.
    The frontend can connect here to see the progress.
    """
    await websocket.accept()

    try:
        while True:
            # Enviamos el progreso cada 500ms
            # We send the progress every 500ms
            progress_data = {
                "status": _current_progress.status,
                "total_pages": _current_progress.total_pages,
                "processed_pages": _current_progress.processed_pages,
                "current_page": _current_progress.current_page,
                "documents_found": _current_progress.documents_found,
                "errors": _current_progress.errors,
                "percentage": round(_current_progress.percentage, 1)
            }
            await websocket.send_json(progress_data)

            # Si ya terminó, esperamos un poco y cerramos
            # If it's already finished, we wait a bit and close
            if _current_progress.status in ["done", "error"]:
                await asyncio.sleep(1)
                break

            await asyncio.sleep(0.5)

    except WebSocketDisconnect:
        logger.debug("WebSocket de progreso desconectado")
    except Exception as e:
        logger.error(f"Error en WebSocket de progreso: {e}")


@router.post("/clear-cache")
async def clear_extraction_cache():
    """Limpia el caché de resultados de extracción.

    Clears the extraction results cache.
    """
    clear_cache()
    return {"message": "Caché limpiado exitosamente"}
