"""
Servicio para convertir PDFs a imágenes.
Necesitamos esto porque la IA "ve" mejor las cédulas en formato imagen.
"""

import fitz  # PyMuPDF - librería rápida para trabajar con PDFs
import io
from typing import List, Optional

def convert_pdf_to_images(pdf_bytes: bytes, dpi: int = 150) -> List[bytes]:
    """
    Convierte un PDF en bytes a una lista de imágenes.

    Args:
        pdf_bytes: El archivo PDF en formato de bytes
        dpi: Calidad de la imagen (150 es suficiente para leer cédulas)

    Returns:
        Lista de imágenes en formato bytes
    """

    images_list = []

    try:
        # Abrimos el PDF en memoria (no creamos archivo temporal)
        # Esto es más rápido y no llena la computadora de archivos basura
        document = fitz.open(stream=pdf_bytes, filetype="pdf")

        # Recorremos cada página del PDF
        for page_num, page in enumerate(document):
            try:
                # Convertimos la página a imagen
                # zoom=2 significa que la imagen será 2 veces más grande que el original
                # Esto ayuda a que la IA lea mejor los textos pequeños
                zoom = dpi / 72  # 72 es el DPI por defecto de PDF
                mat = fitz.Matrix(zoom, zoom)

                # Generamos la imagen de la página
                pix = page.get_pixmap(matrix=mat)

                # Convertimos la imagen a bytes en formato PNG
                # PNG es mejor que JPEG para textos porque no pierde calidad
                img_bytes = pix.tobytes(output="png")

                # Agregamos la imagen a nuestra lista
                images_list.append(img_bytes)

                # Liberamos memoria borrando la imagen temporal
                del pix

            except Exception as e:
                # Si falla una página, no nos detenemos
                # Simplemente seguimos con las demás
                print(f"Error en página {page_num + 1}: {e}")
                continue

        # Cerramos el documento para liberar memoria
        document.close()

        # Si no se pudo convertir ninguna página, devolvemos una lista vacía
        if not images_list:
            print("No se pudo convertir ninguna página del PDF")

        return images_list

    except Exception as e:
        # Si falla todo el proceso, devolvemos una lista vacía
        # El programa principal se encargará de avisar del error
        print(f"Error al procesar el PDF: {e}")
        return []
