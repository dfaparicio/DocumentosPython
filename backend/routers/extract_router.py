"""
Router que define el endpoint para procesar PDFs de documentos colombianos.
Este es el punto donde la API recibe el archivo y coordina todo el proceso.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from services.pdf_service import convert_pdf_to_images
from services.ai_service import extract_data_from_image, extract_data_from_two_faces
from services.excel_service import create_excel_with_merged_documents
from services.document_builder import DocumentBuilder
from services.data_merger import merge_face_data, merge_one_face_data, clean_merged_data
from services.document_validator import get_validator

# Creamos el router
# El router agrupa los endpoints relacionados con extracción de datos
router = APIRouter(prefix="/extract", tags=["extracción"])

@router.post("/")
async def extract_from_pdf(pdf_file: UploadFile = File(...)):
    """
    Endpoint principal: recibe un PDF de documentos colombianos y devuelve un Excel con los datos extraídos.

    Proceso:
    1. Convierte el PDF a imágenes
    2. Clasifica cada página (FRONTAL, TRASERA, COMPLETO, MIXTO)
    3. Agrupa las páginas en documentos lógicos (Try-Face-First)
    4. Extrae datos usando prompts específicos por tipo de documento y cara
    5. Combina datos de múltiples caras del mismo documento
    6. Genera Excel con el orden correcto de columnas

    Args:
        pdf_file: El archivo PDF enviado por el usuario

    Returns:
        Un archivo Excel para descargar con los datos de todos los documentos
    """

    # Verificamos que el archivo sea un PDF
    if not pdf_file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="El archivo debe ser un PDF"
        )

    try:
        # PASO 1: Leemos el PDF y lo convertimos a imágenes
        pdf_bytes = await pdf_file.read()
        images_list = convert_pdf_to_images(pdf_bytes)

        if not images_list:
            raise HTTPException(
                status_code=400,
                detail="No se pudo procesar el PDF. Asegúrate de que el archivo es válido."
            )

        print(f"PDF convertido a {len(images_list)} imágenes")

        # PASO 2: Construimos documentos lógicos usando el algoritmo Try-Face-First
        builder = DocumentBuilder()
        documents = builder.process_pdf_pages(images_list)

        print(f"Se construyeron {len(documents)} documentos")

        # Imprimimos estadísticas
        stats = builder.get_statistics()
        print(f"Estadísticas: {stats}")

        # PASO 3: Extraemos datos de cada documento
        validator = get_validator()
        merged_data_list = []

        for doc in documents:
            document_type = doc.document_type
            is_two_face = validator.is_two_face_document(document_type)

            if doc.is_one_face or not is_two_face:
                # Documento de 1 cara (ej: pasaporte, contraseña)
                if doc.front_face:
                    data = extract_data_from_image(doc.front_face, document_type, "completo")
                    merged = merge_one_face_data(data, document_type)
                    merged = clean_merged_data(merged)
                    merged_data_list.append(merged)
                    print(f"Documento 1 cara procesado: {document_type}")

            else:
                # Documento de 2 caras
                if doc.front_face and doc.back_face:
                    # Extraemos datos de ambas caras con prompts específicos
                    frontal_data, trasera_data = extract_data_from_two_faces(
                        doc.front_face, doc.back_face, document_type
                    )

                    # Validamos consistencia
                    validation_result = validator.validate_document_consistency(
                        frontal_data, trasera_data, document_type
                    )

                    if validation_result.errors:
                        print(f"Errores de validación en documento {document_type}: {validation_result.errors}")

                    if validation_result.warnings:
                        print(f"Advertencias en documento {document_type}: {validation_result.warnings}")

                    # Combinamos datos
                    merged = merge_face_data(frontal_data, trasera_data, document_type)
                    merged = clean_merged_data(merged)
                    merged_data_list.append(merged)
                    print(f"Documento 2 caras procesado: {document_type}")

                else:
                    # Faltan caras, usamos lo que tenemos
                    if doc.front_face:
                        data = extract_data_from_image(doc.front_face, document_type, "frontal")
                        merged = merge_one_face_data(data, document_type)
                        merged = clean_merged_data(merged)
                        merged_data_list.append(merged)
                        print(f"Documento incompleto (solo frontal): {document_type}")

        # PASO 4: Creamos el Excel con todos los datos combinados
        if not merged_data_list:
            raise HTTPException(
                status_code=400,
                detail="No se pudo extraer ningún dato de los documentos."
            )

        print(f"Generando Excel con {len(merged_data_list)} documentos")

        excel_buffer = create_excel_with_merged_documents(merged_data_list)

        # PASO 5: Devolvemos el Excel al usuario
        return StreamingResponse(
            excel_buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": "attachment; filename=documentos_extraidos.xlsx"
            }
        )

    except HTTPException:
        # Si es un error que ya controlamos, lo relanzamos
        raise

    except Exception as e:
        # Si algo inesperado falla, devolvemos un error genérico
        print(f"Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail="Ocurrió un error al procesar el archivo. Por favor intenta de nuevo."
        )

