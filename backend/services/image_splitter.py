"""
Divisor de imágenes para páginas mixtas.
Divide una imagen que contiene dos caras de un documento en dos imágenes separadas.
"""

import io
from typing import Dict, Tuple, Optional
from PIL import Image


def split_image_by_coordinates(image_bytes: bytes, coordinates: Dict[str, Dict[str, any]]) -> Optional[Tuple[bytes, bytes]]:
    """
    Divide una imagen en dos usando las coordenadas especificadas.

    Args:
        image_bytes: La imagen original en formato bytes
        coordinates: Diccionario con coordenadas de cara_1 y cara_2
            Ejemplo: {
                "cara_1": {"y_inicio": 0, "y_fin": 500, "x_inicio": 0, "x_fin": 1000},
                "cara_2": {"y_inicio": 500, "y_fin": 1000, "x_inicio": 0, "x_fin": 1000}
            }

    Returns:
        Tupla (cara_1, cara_2) con las dos imágenes en bytes, o None si falla
    """
    try:
        # Cargamos la imagen desde bytes
        image = Image.open(io.BytesIO(image_bytes))

        # Verificamos que la imagen esté en modo RGBA para mantener transparencia si existe
        if image.mode != 'RGBA':
            image = image.convert('RGBA')

        # Obtenemos las dimensiones
        width, height = image.size

        # Extraemos cara 1
        coords1 = coordinates.get("cara_1", {})
        y1_start = int(coords1.get("y_inicio", 0))
        y1_end = int(coords1.get("y_fin", height // 2))
        x1_start = int(coords1.get("x_inicio", 0))
        x1_end = int(coords1.get("x_fin", width))

        # Validamos y ajustamos las coordenadas
        y1_start = max(0, min(y1_start, height))
        y1_end = max(y1_start, min(y1_end, height))
        x1_start = max(0, min(x1_start, width))
        x1_end = max(x1_start, min(x1_end, width))

        # Recortamos cara 1
        box1 = (x1_start, y1_start, x1_end, y1_end)
        cara1_image = image.crop(box1)

        # Convertimos a PNG en bytes
        cara1_bytes = io.BytesIO()
        cara1_image.save(cara1_bytes, format='PNG')
        cara1_bytes = cara1_bytes.getvalue()

        # Extraemos cara 2
        coords2 = coordinates.get("cara_2", {})
        y2_start = int(coords2.get("y_inicio", height // 2))
        y2_end = int(coords2.get("y_fin", height))
        x2_start = int(coords2.get("x_inicio", 0))
        x2_end = int(coords2.get("x_fin", width))

        # Validamos y ajustamos las coordenadas
        y2_start = max(0, min(y2_start, height))
        y2_end = max(y2_start, min(y2_end, height))
        x2_start = max(0, min(x2_start, width))
        x2_end = max(x2_start, min(x2_end, width))

        # Recortamos cara 2
        box2 = (x2_start, y2_start, x2_end, y2_end)
        cara2_image = image.crop(box2)

        # Convertimos a PNG en bytes
        cara2_bytes = io.BytesIO()
        cara2_image.save(cara2_bytes, format='PNG')
        cara2_bytes = cara2_bytes.getvalue()

        return (cara1_bytes, cara2_bytes)

    except Exception as e:
        print(f"Error al dividir imagen: {e}")
        return None


def split_image_vertically(image_bytes: bytes, split_at: Optional[int] = None) -> Optional[Tuple[bytes, bytes]]:
    """
    Divide una imagen verticalmente en dos partes iguales (o en una posición específica).

    Args:
        image_bytes: La imagen original en formato bytes
        split_at: Posición Y donde dividir (None para dividir en la mitad)

    Returns:
        Tupla (parte_superior, parte_inferior) con las dos imágenes en bytes, o None si falla
    """
    try:
        # Cargamos la imagen desde bytes
        image = Image.open(io.BytesIO(image_bytes))

        # Verificamos que la imagen esté en modo RGBA
        if image.mode != 'RGBA':
            image = image.convert('RGBA')

        # Obtenemos las dimensiones
        width, height = image.size

        # Determinamos el punto de división
        if split_at is None:
            split_at = height // 2
        else:
            split_at = max(0, min(split_at, height))

        # Dividimos verticalmente (arriba y abajo)
        # Parte superior
        box_top = (0, 0, width, split_at)
        top_image = image.crop(box_top)

        top_bytes = io.BytesIO()
        top_image.save(top_bytes, format='PNG')
        top_bytes = top_bytes.getvalue()

        # Parte inferior
        box_bottom = (0, split_at, width, height)
        bottom_image = image.crop(box_bottom)

        bottom_bytes = io.BytesIO()
        bottom_image.save(bottom_bytes, format='PNG')
        bottom_bytes = bottom_bytes.getvalue()

        return (top_bytes, bottom_bytes)

    except Exception as e:
        print(f"Error al dividir imagen verticalmente: {e}")
        return None


def split_image_horizontally(image_bytes: bytes, split_at: Optional[int] = None) -> Optional[Tuple[bytes, bytes]]:
    """
    Divide una imagen horizontalmente en dos partes iguales (o en una posición específica).

    Args:
        image_bytes: La imagen original en formato bytes
        split_at: Posición X donde dividir (None para dividir en la mitad)

    Returns:
        Tupla (parte_izquierda, parte_derecha) con las dos imágenes en bytes, o None si falla
    """
    try:
        # Cargamos la imagen desde bytes
        image = Image.open(io.BytesIO(image_bytes))

        # Verificamos que la imagen esté en modo RGBA
        if image.mode != 'RGBA':
            image = image.convert('RGBA')

        # Obtenemos las dimensiones
        width, height = image.size

        # Determinamos el punto de división
        if split_at is None:
            split_at = width // 2
        else:
            split_at = max(0, min(split_at, width))

        # Dividimos horizontalmente (izquierda y derecha)
        # Parte izquierda
        box_left = (0, 0, split_at, height)
        left_image = image.crop(box_left)

        left_bytes = io.BytesIO()
        left_image.save(left_bytes, format='PNG')
        left_bytes = left_bytes.getvalue()

        # Parte derecha
        box_right = (split_at, 0, width, height)
        right_image = image.crop(box_right)

        right_bytes = io.BytesIO()
        right_image.save(right_bytes, format='PNG')
        right_bytes = right_bytes.getvalue()

        return (left_bytes, right_bytes)

    except Exception as e:
        print(f"Error al dividir imagen horizontalmente: {e}")
        return None


def crop_image(image_bytes: bytes, x: int, y: int, width: int, height: int) -> Optional[bytes]:
    """
    Recorta una imagen a las dimensiones especificadas.

    Args:
        image_bytes: La imagen original en formato bytes
        x: Coordenada X inicial
        y: Coordenada Y inicial
        width: Ancho del recorte
        height: Altura del recorte

    Returns:
        La imagen recortada en bytes, o None si falla
    """
    try:
        # Cargamos la imagen desde bytes
        image = Image.open(io.BytesIO(image_bytes))

        # Verificamos que la imagen esté en modo RGBA
        if image.mode != 'RGBA':
            image = image.convert('RGBA')

        # Recortamos la imagen
        box = (x, y, x + width, y + height)
        cropped_image = image.crop(box)

        # Convertimos a PNG en bytes
        cropped_bytes = io.BytesIO()
        cropped_image.save(cropped_bytes, format='PNG')
        cropped_bytes = cropped_bytes.getvalue()

        return cropped_bytes

    except Exception as e:
        print(f"Error al recortar imagen: {e}")
        return None
