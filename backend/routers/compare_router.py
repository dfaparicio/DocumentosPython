"""
Router para comparación y reconciliación de archivos Excel.
Compara dos archivos buscando inconsistencias y guarda el reporte en MongoDB.

Router for comparison and reconciliation of Excel files.
Compares two files for inconsistencies and saves the report to MongoDB.
"""

import logging
from datetime import datetime

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends

from core.auth_middleware import require_active_user
from infrastructure.storage.database import get_database
from services.compare_service import (
    parse_excel_for_comparison,
    reconcile,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/compare", tags=["comparación"])


@router.post("/reconcile")
async def reconcile_files(
    file_a: UploadFile = File(..., description="Primer archivo Excel"),
    file_b: UploadFile = File(..., description="Segundo archivo Excel"),
    user: dict = Depends(require_active_user),
):
    """
    Compara dos archivos Excel buscando inconsistencias.
    Empareja por número de cédula y compara campo a campo.
    Guarda el reporte en MongoDB y devuelve JSON con estadísticas y detalle de discrepancias.

    Compares two Excel files for inconsistencies.
    Matches by document number and compares field by field.
    Saves the report to MongoDB and returns JSON with statistics and discrepancy details.
    """
    for f in [file_a, file_b]:
        if not f.filename.lower().endswith(('.xlsx', '.xls')):
            raise HTTPException(
                status_code=400,
                detail=f"El archivo '{f.filename}' debe ser un Excel (.xlsx o .xls)"
            )

    try:
        bytes_a = await file_a.read()
        bytes_b = await file_b.read()

        # Parsear ambos archivos
        data_a = parse_excel_for_comparison(bytes_a)
        data_b = parse_excel_for_comparison(bytes_b)

        if not data_a:
            raise HTTPException(status_code=400, detail="El Archivo A no contiene datos válidos")
        if not data_b:
            raise HTTPException(status_code=400, detail="El Archivo B no contiene datos válidos")

        logger.info(f"Reconciliando: Archivo A ({len(data_a)}) vs Archivo B ({len(data_b)})")

        # Reconciliar
        result = reconcile(data_a, data_b)

        # Construir respuesta JSON con todo el detalle
        discrepancies = []
        for rc in result.matched:
            if not rc.all_match:
                fields_detail = []
                for fc in rc.fields:
                    fields_detail.append({
                        "campo": fc.field_name,
                        "valor_a": fc.value_a,
                        "valor_b": fc.value_b,
                        "coincide": fc.matches,
                    })
                discrepancies.append({
                    "cedula": rc.document_number,
                    "campos_diferentes": rc.mismatches,
                    "detalle": fields_detail,
                })

        # Registros sin par
        only_in_a = [
            {
                "cedula": r.get("numero_documento", ""),
                "nombres": r.get("nombres", ""),
                "apellidos": r.get("apellidos", ""),
            }
            for r in result.only_in_a
        ]
        only_in_b = [
            {
                "cedula": r.get("numero_documento", ""),
                "nombres": r.get("nombres", ""),
                "apellidos": r.get("apellidos", ""),
            }
            for r in result.only_in_b
        ]

        stats = {
            "total_registros_1": result.stats["total_records_a"],
            "total_registros_2": result.stats["total_records_b"],
            "cedulas_archivo_1": result.stats["cedulas_archivo_1"],
            "cedulas_archivo_2": result.stats["cedulas_archivo_2"],
            "emparejados": result.stats["matched_pairs"],
            "solo_en_1": result.stats["only_in_a"],
            "solo_en_2": result.stats["only_in_b"],
            "registros_con_diferencias": result.stats["records_with_mismatches"],
            "discrepancias_por_campo": {
                label: result.stats["field_mismatch_counts"].get(key, 0)
                for key, label in [
                    ("tipo_documento", "Tipo de Documento"),
                    ("nombres", "Nombres"),
                    ("apellidos", "Apellidos"),
                    ("fecha_nacimiento", "Fecha de Nacimiento"),
                    ("sexo", "Sexo"),
                    ("nacionalidad", "Nacionalidad"),
                ]
            },
        }

        # Guardar reporte en MongoDB (colección "reports")
        db = get_database()
        report_doc = {
            "user_email": user["email"],
            "created_at": datetime.utcnow(),
            "file_a_name": file_a.filename,
            "file_b_name": file_b.filename,
            "all_clear": result.stats["all_clear"],
            "stats": stats,
            "discrepancias": discrepancies,
            "solo_en_1_detalle": only_in_a,
            "solo_en_2_detalle": only_in_b,
        }
        insert_result = await db["reports"].insert_one(report_doc)
        report_id = str(insert_result.inserted_id)

        logger.info(
            f"Resultado: {result.stats['matched_pairs']} pares coincidentes, "
            f"{result.stats['only_in_a']} solo en 1, {result.stats['only_in_b']} solo en 2, "
            f"report_id={report_id}"
        )

        return {
            "report_id": report_id,
            "all_clear": result.stats["all_clear"],
            "stats": stats,
            "discrepancias": discrepancies,
            "solo_en_1_detalle": only_in_a,
            "solo_en_2_detalle": only_in_b,
        }

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Error en reconciliación: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error al comparar los archivos: {str(e)}"
        )
