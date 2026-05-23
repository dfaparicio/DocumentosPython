"""
Servicio para convertir PDFs a imágenes optimizadas.
Usa JPEG en vez de PNG para reducir tamaño (~10x más pequeño).
DPI reducido a 100 (suficiente para OCR de documentos).

Service for converting PDFs to optimized images.
Uses JPEG instead of PNG to reduce size (~10x smaller).
Reduced DPI to 100 (sufficient for document OCR).
"""

import fitz  # PyMuPDF
import io
import logging
from typing import List
from PIL import Image

logger = logging.getLogger(__name__)


def convert_pdf_to_images(pdf_bytes: bytes, dpi: int = 100) -> List[bytes]:
    """
    Convierte un PDF en bytes a una lista de imágenes JPEG optimizadas.

    Args:
        pdf_bytes: El archivo PDF en formato de bytes
        dpi: Calidad de la imagen (100 es suficiente para leer documentos)

    Returns:
        Lista de imágenes en formato bytes (JPEG)

    Converts a PDF in bytes to a list of optimized JPEG images.

    Args:
        pdf_bytes: The PDF file in byte format
        dpi: Image quality (100 is sufficient for reading documents)

    Returns:
        List of images in byte format (JPEG)
    """
    images_list = []

    try:
        document = fitz.open(stream=pdf_bytes, filetype="pdf")

        for page_num, page in enumerate(document):
            try:
                # Convertimos la página a imagen
                # We convert the page to an image
                zoom = dpi / 72  # 72 es el DPI por defecto de PDF
                # 72 is the default PDF DPI
                mat = fitz.Matrix(zoom, zoom)

                # Generamos la imagen de la página
                # We generate the page image
                pix = page.get_pixmap(matrix=mat)

                # Convertimos a JPEG usando Pillow para controlar calidad
                # JPEG es ~10x más pequeño que PNG con calidad suficiente para OCR
                # We convert to JPEG using Pillow to control quality
                # JPEG is ~10x smaller than PNG with sufficient quality for OCR
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

                # Guardamos como JPEG con quality=85 (buen balance tamaño/calidad)
                # We save as JPEG with quality=85 (good size/quality balance)
                img_buffer = io.BytesIO()
                img.save(img_buffer, format="JPEG", quality=85, optimize=True)
                img_bytes = img_buffer.getvalue()

                images_list.append(img_bytes)

                # Liberamos memoria
                # We free memory
                del pix
                del img
                del img_buffer

                logger.debug(f"Página {page_num + 1} convertida ({len(img_bytes)} bytes)")

            except Exception as e:
                logger.error(f"Error en página {page_num + 1}: {e}")
                continue

        document.close()

        if not images_list:
            logger.warning("No se pudo convertir ninguna página del PDF")

        return images_list

    except Exception as e:
        logger.error(f"Error al procesar el PDF: {e}")
        return []
