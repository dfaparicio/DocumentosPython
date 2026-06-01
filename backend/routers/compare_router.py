"""
Router para comparación y reconciliación de archivos Excel.
Permite mezclar un Excel y comparar dos archivos buscando inconsistencias.

Router for comparison and reconciliation of Excel files.
Allows shuffling an Excel and comparing two files for inconsistencies.
"""

import uuid
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse

from services.compare_service import (
    parse_excel_for_comparison,
    reconcile,
    create_reconciliation_excel,
)
from services.reference_generator import generate_shuffled_excel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/compare", tags=["comparación"])

# Cache temporal de reportes generados (clave -> bytes del Excel)
# Temporary cache of generated reports (key -> Excel bytes)
_report_cache: dict = {}


@router.post("/shuffle")
async def shuffle_excel(file: UploadFile = File(...)):
    """
    Recibe un Excel y devuelve el mismo con las filas en orden aleatorio.

    Receives an Excel and returns it with rows in random order.
    """
    if not file.filename.lower().endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=400,
            detail="El archivo debe ser un Excel (.xlsx o .xls)"
        )

    try:
        file_bytes = await file.read()

        output = generate_shuffled_excel(file_bytes)

        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": "attachment; filename=documentos_mezclados.xlsx"
            }
        )

    except Exception as e:
        logger.error(f"Error al mezclar Excel: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar el archivo: {str(e)}"
        )


@router.post("/reconcile")
async def reconcile_files(
    file_a: UploadFile = File(..., description="Primer archivo Excel"),
    file_b: UploadFile = File(..., description="Segundo archivo Excel"),
):
    """
    Compara dos archivos Excel buscando inconsistencias.
    Empareja por número de cédula y compara campo a campo.
    Devuelve JSON con estadísticas y detalle de discrepancias.

    Compares two Excel files for inconsistencies.
    Matches by document number and compares field by field.
    Returns JSON with statistics and discrepancy details.
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

        # Generar Excel y guardarlo en cache
        output = create_reconciliation_excel(result)
        report_id = str(uuid.uuid4())[:8]
        output.seek(0)
        _report_cache[report_id] = output.read()

        logger.info(
            f"Resultado: {result.stats['matched_pairs']} pares, "
            f"{result.stats['mismatching_fields']} diferencias, "
            f"{result.stats['accuracy_pct']}% precisión, report_id={report_id}"
        )

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

        return {
            "report_id": report_id,
            "all_clear": result.stats["all_clear"],
            "stats": {
                "total_registros_a": result.stats["total_records_a"],
                "total_registros_b": result.stats["total_records_b"],
                "emparejados": result.stats["matched_pairs"],
                "solo_en_a": result.stats["only_in_a"],
                "solo_en_b": result.stats["only_in_b"],
                "campos_comparados": result.stats["total_fields_compared"],
                "campos_coincidentes": result.stats["matching_fields"],
                "campos_diferentes": result.stats["mismatching_fields"],
                "registros_con_diferencias": result.stats["records_with_mismatches"],
                "precision_pct": result.stats["accuracy_pct"],
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
            },
            "discrepancias": discrepancies,
            "solo_en_a_detalle": only_in_a,
            "solo_en_b_detalle": only_in_b,
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


@router.get("/download/{report_id}")
async def download_report(report_id: str):
    """
    Descarga el Excel de conciliación generado previamente.

    Downloads the previously generated reconciliation Excel.
    """
    if report_id not in _report_cache:
        raise HTTPException(status_code=404, detail="Reporte no encontrado. Realiza una nueva comparación.")

    from io import BytesIO
    excel_bytes = _report_cache[report_id]

    return StreamingResponse(
        BytesIO(excel_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=conciliacion_reporte.xlsx"
        }
    )
