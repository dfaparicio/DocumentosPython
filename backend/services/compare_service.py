"""
Servicio de reconciliación entre dos archivos Excel de documentos.
Compara los datos emparejando por número de cédula y reporta discrepancias.

Reconciliation service between two document Excel files.
Compares data by matching document numbers and reports discrepancies.
"""

import io
import re
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass, field

import pandas as pd

logger = logging.getLogger(__name__)

# Campos a comparar (clave interna -> nombre legible)
COMPARE_FIELDS = [
    ("tipo_documento", "Tipo de Documento"),
    ("nombres", "Nombres"),
    ("apellidos", "Apellidos"),
    ("fecha_nacimiento", "Fecha de Nacimiento"),
    ("sexo", "Sexo"),
    ("nacionalidad", "Nacionalidad"),
]

# Aliases de columnas: múltiples nombres posibles para cada campo interno
# Permite comparar Excels con diferentes nombres de columnas
# Column aliases: multiple possible names for each internal field
COLUMN_ALIASES = {
    "no": [
        "no.", "no", "numero", "consecutivo", "#", "item", "num",
    ],
    "tipo_documento": [
        "tipo de documento", "tipo documento", "tipo doc",
        "tipo", "clase de documento", "clase documento",
        "tipo de doc", "td", "tipodoc",
        # Alias del archivo externo (SENA / registros externos)
        "tipo de identificacion", "tipo identificacion",
        "tipo id", "tipo de id",
    ],
    "numero_documento": [
        "numero de documento", "numero documento", "num documento",
        "cedula", "documento", "no. documento", "no documento",
        "numero de cedula", "numero cedula",
        "cc", "nit", "dni", "cedula de ciudadania",
        "identificacion", "numero de identificacion",
        "num identificacion", "numero identificacion",
        "doc", "doc identidad", "documento de identidad",
        "numero de cc", "no. cc", "ced",
    ],
    "nombres": [
        "nombres", "nombre", "nombre(s)", "primer nombre",
        "name", "nomb", "nom", "name(s)",
    ],
    "apellidos": [
        "apellidos", "apellido", "apellido(s)", "primer apellido",
        "last name", "ape", "ape(s)",
    ],
    "fecha_nacimiento": [
        "fecha de nacimiento", "fecha nacimiento", "f. nacimiento",
        "fn", "fecha nac", "nacimiento", "fecha de nac",
        "f. nac", "born", "birthdate", "birth date",
        "fecha", "f.n",
    ],
    "sexo": [
        "sexo", "genero", "sex", "g", "gen",
    ],
    "nacionalidad": [
        "nacionalidad", "nacion", "nacional", "nationality",
    ],
    "estado": [
        "estado", "status", "state",
    ],
    "pagina_origen": [
        "pagina origen", "pagina", "hoja origen", "page", "pag",
    ],
    "confianza": [
        "confianza", "confidence", "conf",
    ],
}


@dataclass
class FieldComparison:
    """Resultado de comparar un campo entre dos registros."""
    field_name: str
    value_a: str
    value_b: str
    matches: bool


@dataclass
class RecordComparison:
    """Resultado de comparar dos registros emparejados."""
    document_number: str
    fields: List[FieldComparison] = field(default_factory=list)
    all_match: bool = True
    mismatches: int = 0


@dataclass
class ReconciliationResult:
    """Resultado completo de la reconciliación."""
    matched: List[RecordComparison] = field(default_factory=list)
    only_in_a: List[Dict] = field(default_factory=list)
    only_in_b: List[Dict] = field(default_factory=list)
    stats: Dict = field(default_factory=dict)


def _clean_value(val) -> str:
    """
    Limpia un valor de celda de Excel: elimina NaN, floats .0, etc.
    Cleans an Excel cell value: removes NaN, float .0, etc.
    """
    if pd.isna(val):
        return ""
    val_str = str(val).strip()
    # Eliminar sufijo .0 de números almacenados como float en Excel
    if val_str.endswith(".0") and val_str != ".0":
        try:
            # Verificar que es realmente un float antes de quitar .0
            float(val_str)
            val_str = val_str[:-2]
        except ValueError:
            pass
    # Eliminar valores "nan" que pandas genera a veces
    if val_str.lower() == "nan":
        return ""
    return val_str


def _normalize_col_name(col: str) -> str:
    """
    Normaliza un nombre de columna: minúsculas, sin acentos, sin espacios extra.
    Normalizes a column name: lowercase, no accents, no extra spaces.
    """
    col = col.strip().lower()
    # Quitar acentos para matching tolerante
    replacements = {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ü': 'u', 'ñ': 'n'}
    for accented, plain in replacements.items():
        col = col.replace(accented, plain)
    # Colapsar espacios múltiples
    return re.sub(r'\s+', ' ', col)


def _match_columns(excel_columns: List[str]) -> Dict[str, str]:
    """
    Dado los nombres de columnas del Excel (ya normalizados),
    busca coincidencias contra los aliases y retorna {clave_interna: nombre_columna_excel}.

    Given Excel column names (already normalized),
    matches against aliases and returns {internal_key: excel_column_name}.
    """
    matched = {}
    used_cols = set()

    for key, alias_list in COLUMN_ALIASES.items():
        for alias in alias_list:
            alias_norm = _normalize_col_name(alias)
            alias_no_spaces = alias_norm.replace(" ", "")
            for col in excel_columns:
                col_no_spaces = col.replace(" ", "")
                if col not in used_cols and (col == alias_norm or col_no_spaces == alias_no_spaces):
                    matched[key] = col
                    used_cols.add(col)
                    break
            if key in matched:
                break

    return matched


def _auto_detect_doc_column(df, matched: Dict[str, str]) -> Optional[str]:
    """
    Si no se encontró la columna de documento por alias,
    busca la primera columna que tenga valores que parezcan números de cédula (6+ dígitos).

    If the document column wasn't found by alias,
    finds the first column with values that look like ID numbers (6+ digits).
    """
    if "numero_documento" in matched:
        return None

    used_cols = set(matched.values())
    for col in df.columns:
        if col in used_cols:
            continue
        # Verificar si la mayoría de valores parecen números de documento
        numeric_count = 0
        sample = df[col].dropna().head(20)
        for val in sample:
            val_str = _clean_value(val)
            # Número de cédula: 6-12 dígitos, puede tener puntos
            digits = re.sub(r'[.\s\-]', '', val_str)
            if digits.isdigit() and 6 <= len(digits) <= 15:
                numeric_count += 1
        if len(sample) > 0 and numeric_count / len(sample) >= 0.5:
            logger.info(f"Autodetección: columna '{col}' parece ser numero_documento")
            return col

    return None


def _detect_header_row(file_bytes: bytes, sheet_name) -> int:
    """
    Detecta la fila del encabezado en un Excel.
    Algunos archivos tienen filas de título antes de los encabezados reales.
    Busca la primera fila que contenga nombres de columna reconocidos.

    Detects the header row in an Excel file.
    Some files have title rows before the actual headers.
    Finds the first row containing recognized column names.
    """
    # Leer las primeras filas sin encabezado para inspeccionar
    try:
        df_raw = pd.read_excel(
            io.BytesIO(file_bytes), sheet_name=sheet_name,
            header=None, nrows=10
        )
    except Exception:
        return 0

    # Construir set de todos los aliases normalizados
    all_aliases = set()
    for alias_list in COLUMN_ALIASES.values():
        for alias in alias_list:
            all_aliases.add(_normalize_col_name(alias))

    best_row = 0
    best_matches = 0

    for row_idx in range(min(8, len(df_raw))):
        row_values = df_raw.iloc[row_idx]
        match_count = 0
        for val in row_values:
            if pd.isna(val):
                continue
            normalized = _normalize_col_name(str(val))
            # Verificar si coincide con algún alias conocido
            if normalized in all_aliases:
                match_count += 1
            else:
                # Verificar sin espacios también
                no_spaces = normalized.replace(" ", "")
                for alias in all_aliases:
                    if alias.replace(" ", "") == no_spaces:
                        match_count += 1
                        break

        if match_count > best_matches:
            best_matches = match_count
            best_row = row_idx

    logger.info(
        f"Detección de encabezado: fila {best_row} con {best_matches} "
        f"coincidencias de columnas conocidas"
    )
    return best_row


def parse_excel_for_comparison(file_bytes: bytes) -> List[Dict]:
    """
    Lee un Excel y extrae los datos normalizados para comparación.
    Soporta cualquier nombre de columna — usa aliases flexibles para encontrar cada campo.
    Detecta automáticamente la fila de encabezados (soporta archivos con títulos previos).

    Reads an Excel and extracts normalized data for comparison.
    Supports any column name — uses flexible aliases to find each field.
    Auto-detects the header row (supports files with title rows before headers).
    """
    # Determinar la hoja a usar
    sheet_name = "Documentos"
    try:
        pd.read_excel(io.BytesIO(file_bytes), sheet_name=sheet_name, nrows=0)
    except Exception:
        sheet_name = 0

    # Detectar la fila del encabezado automáticamente
    header_row = _detect_header_row(file_bytes, sheet_name)

    logger.info(f"Leyendo Excel con header en fila {header_row}, hoja='{sheet_name}'")
    df = pd.read_excel(
        io.BytesIO(file_bytes), sheet_name=sheet_name, header=header_row
    )

    # Normalizar nombres de columnas (sin acentos, sin espacios extra)
    df.columns = [_normalize_col_name(str(col)) for col in df.columns]

    logger.info(f"Columnas detectadas en Excel: {list(df.columns)}")
    logger.info(f"Total filas: {len(df)}")

    # Matching flexible de columnas por aliases
    col_mapping = _match_columns(list(df.columns))

    # Autodetección de columna de documento si no se encontró por alias
    auto_doc_col = _auto_detect_doc_column(df, col_mapping)
    if auto_doc_col:
        col_mapping["numero_documento"] = auto_doc_col

    logger.info(f"Mapeo de columnas: {col_mapping}")

    # Mapear columnas
    records = []
    all_keys = set(COLUMN_ALIASES.keys())
    for _, row in df.iterrows():
        record = {}
        for key in all_keys:
            if key in col_mapping:
                record[key] = _clean_value(row.get(col_mapping[key], ""))
            else:
                record[key] = ""

        # Normalizar número de documento para emparejamiento
        record["_doc_normalized"] = _normalize_doc_number(record.get("numero_documento", ""))

        # Solo agregar registros que tengan número de documento
        if record["_doc_normalized"]:
            records.append(record)

    # Log de diagnóstico: mostrar cuántos registros tienen número de documento
    logger.info(f"Registros parseados con numero_documento: {len(records)}")

    # Log de los primeros 3 documentos normalizados para diagnóstico
    for i, r in enumerate(records[:3]):
        logger.debug(
            f"  Registro {i+1}: doc='{r.get('numero_documento', '')}' "
            f"-> normalized='{r.get('_doc_normalized', '')}'"
        )

    return records


def _normalize_doc_number(doc: str) -> str:
    """
    Normaliza un número de documento quitando puntos, espacios y guiones.
    Normalizes a document number by removing dots, spaces, and hyphens.
    """
    if not doc:
        return ""
    return re.sub(r'[.\s\-]', '', doc).strip()


def _normalize_for_comparison(value: str, field_name: str) -> str:
    """
    Normaliza un valor para comparación tolerante.
    Normaliza según el tipo de campo.

    Normalizes a value for tolerant comparison.
    Normalizes based on field type.
    """
    if not value:
        return ""

    value = value.strip().lower()

    if field_name == "fecha_nacimiento":
        return _normalize_date(value)
    elif field_name == "sexo":
        return _normalize_sex(value)
    elif field_name == "tipo_documento":
        return _normalize_doc_type(value)
    else:
        # Quitar acentos para comparación tolerante
        return _remove_accents(value)

def _normalize_doc_type(doc_type: str) -> str:
    """
    Normaliza el tipo de documento agrupando sinónimos.
    """
    doc_type = _remove_accents(doc_type.strip().lower())
    
    # Agrupar por cédula de ciudadanía
    if doc_type in ("cc", "cedula", "cedula de ciudadania", "c.c.", "c.c"):
        return "CC"
    # Agrupar por tarjeta de identidad
    elif doc_type in ("ti", "tarjeta de identidad", "t.i.", "t.i"):
        return "TI"
    # Agrupar por cédula de extranjería
    elif doc_type in ("ce", "cedula de extranjeria", "c.e.", "c.e"):
        return "CE"
    # Agrupar por registro civil
    elif doc_type in ("rc", "registro civil", "r.c.", "r.c"):
        return "RC"
    # Agrupar por PEP
    elif doc_type in ("pep", "permiso especial de permanencia"):
        return "PEP"
    # Agrupar por PPT
    elif doc_type in ("ppt", "permiso de proteccion temporal"):
        return "PPT"
    # Agrupar por pasaporte
    elif doc_type in ("pa", "pasaporte"):
        return "PA"
        
    return doc_type.upper()


def _normalize_date(date_str: str) -> str:
    """
    Normaliza una fecha a formato YYYYMMDD para comparación.
    Normalizes a date to YYYYMMDD format for comparison.
    """
    if not date_str:
        return ""

    date_str = date_str.strip()

    # DD/MM/YYYY
    match = re.match(r'^(\d{1,2})/(\d{1,2})/(\d{4})$', date_str)
    if match:
        return f"{match.group(3)}{match.group(2).zfill(2)}{match.group(1).zfill(2)}"

    # YYYY-MM-DD
    match = re.match(r'^(\d{4})-(\d{1,2})-(\d{1,2})$', date_str)
    if match:
        return f"{match.group(1)}{match.group(2).zfill(2)}{match.group(3).zfill(2)}"

    # DD-MM-YYYY
    match = re.match(r'^(\d{1,2})-(\d{1,2})-(\d{4})$', date_str)
    if match:
        return f"{match.group(3)}{match.group(2).zfill(2)}{match.group(1).zfill(2)}"

    return date_str.lower()


def _normalize_sex(sex: str) -> str:
    """
    Normaliza el campo sexo.
    Normalizes the sex field.
    """
    sex = sex.strip().lower()
    if sex in ("m", "masculino", "male"):
        return "M"
    elif sex in ("f", "femenino", "female"):
        return "F"
    return sex


def _remove_accents(text: str) -> str:
    """
    Quita acentos para comparación tolerante.
    Removes accents for tolerant comparison.
    """
    replacements = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'ü': 'u', 'ñ': 'n',
    }
    for accented, plain in replacements.items():
        text = text.replace(accented, plain)
    return text


def reconcile(file_a_data: List[Dict], file_b_data: List[Dict]) -> ReconciliationResult:
    """
    Reconcilia dos conjuntos de datos comparando por número de documento (cédula).
    Verifica que ambos archivos tengan exactamente las mismas cédulas,
    sin importar el orden. A y B son intercambiables.

    Reconciles two datasets by comparing document numbers.
    Verifies that both files have exactly the same document numbers,
    regardless of order. A and B are interchangeable.
    """
    result = ReconciliationResult()

    # Extraer cédulas normalizadas de cada archivo (como sets para comparación)
    docs_a = {}
    for record in file_a_data:
        doc = record.get("_doc_normalized", "")
        if doc:
            docs_a[doc] = record

    docs_b = {}
    for record in file_b_data:
        doc = record.get("_doc_normalized", "")
        if doc:
            docs_b[doc] = record

    set_a = set(docs_a.keys())
    set_b = set(docs_b.keys())

    logger.info(
        f"Archivo 1 tiene {len(set_a)} cédulas únicas, "
        f"Archivo 2 tiene {len(set_b)} cédulas únicas"
    )
    logger.debug(f"  Docs Archivo 1 (muestra): {list(set_a)[:5]}")
    logger.debug(f"  Docs Archivo 2 (muestra): {list(set_b)[:5]}")

    # Cédulas que están en ambos archivos
    common = set_a & set_b
    # Cédulas solo en Archivo 1
    only_a = set_a - set_b
    # Cédulas solo en Archivo 2
    only_b = set_b - set_a

    # Registros emparejados (cédula encontrada en ambos)
    for doc_num in sorted(common):
        record_a = docs_a[doc_num]
        record_b = docs_b[doc_num]

        comparison = RecordComparison(
            document_number=record_a.get("numero_documento", doc_num)
        )

        # Mostrar campo a campo para los emparejados, validando solo tipo_documento y numero
        for field_key, field_label in COMPARE_FIELDS:
            val_a = record_a.get(field_key, "")
            val_b = record_b.get(field_key, "")

            if field_key == "tipo_documento":
                norm_a = _normalize_for_comparison(val_a, field_key)
                norm_b = _normalize_for_comparison(val_b, field_key)
                matches = (norm_a == norm_b)
                if not matches:
                    comparison.all_match = False
                    comparison.mismatches += 1
            else:
                # Dado que el usuario especificó que para los demás campos no genera inconsistencia,
                # forzamos a que siempre se considere una coincidencia válida.
                matches = True

            comparison.fields.append(FieldComparison(
                field_name=field_label,
                value_a=val_a,
                value_b=val_b,
                matches=matches,
            ))

        result.matched.append(comparison)

    # Registros solo en Archivo 1
    for doc_num in sorted(only_a):
        result.only_in_a.append(docs_a[doc_num])

    # Registros solo en Archivo 2
    for doc_num in sorted(only_b):
        result.only_in_b.append(docs_b[doc_num])

    # Estadísticas
    total_matched = len(common)
    total_only_a = len(only_a)
    total_only_b = len(only_b)
    total_mismatches = sum(1 for m in result.matched if not m.all_match)

    # Calcular discrepancias por campo
    field_mismatch_counts = {field_key: 0 for field_key, _ in COMPARE_FIELDS}
    for m in result.matched:
        for fc in m.fields:
            if not fc.matches:
                # Buscar la clave interna del campo
                for fk, fl in COMPARE_FIELDS:
                    if fl == fc.field_name:
                        field_mismatch_counts[fk] += 1
                        break

    # all_clear = ambos archivos tienen exactamente las mismas cédulas
    all_clear = total_only_a == 0 and total_only_b == 0

    result.stats = {
        "total_records_a": len(file_a_data),
        "total_records_b": len(file_b_data),
        "cedulas_archivo_1": len(set_a),
        "cedulas_archivo_2": len(set_b),
        "matched_pairs": total_matched,
        "only_in_a": total_only_a,
        "only_in_b": total_only_b,
        "records_with_mismatches": total_mismatches,
        "records_all_match": total_matched - total_mismatches,
        "field_mismatch_counts": field_mismatch_counts,
        "all_clear": all_clear,
    }

    return result
