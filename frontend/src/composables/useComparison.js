import axios from 'axios'
import { useComparisonStore } from '../stores/comparison'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export function useComparison() {
  const store = useComparisonStore()

  /**
   * Mezcla un Excel y devuelve la versión con filas aleatorias.
   */
  const shuffleExcel = async (file) => {
    try {
      store.setLoading(true, 'Mezclando filas...')

      const formData = new FormData()
      formData.append('file', file)

      const response = await axios.post(`${API_URL}/compare/shuffle`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        responseType: 'blob',
      })

      const now = new Date()
      const dateStr = now.toISOString().split('T')[0]
      const timeStr = now.toTimeString().split(' ')[0].replace(/:/g, '-')
      const fileName = `documentos_mezclados_${dateStr}_${timeStr}.xlsx`

      store.setShuffledFile(response.data, fileName)
      store.setSuccess('✅ Excel mezclado correctamente. Se descargó automáticamente.')

      // Auto-descargar
      _downloadBlob(response.data, fileName)

    } catch (err) {
      console.error('Error al mezclar:', err)
      store.setError(_extractErrorMessage(err))
    } finally {
      store.setLoading(false)
    }
  }

  /**
   * Compara dos archivos Excel. Devuelve JSON con stats y discrepancias.
   */
  const reconcileFiles = async (fileA, fileB) => {
    try {
      store.setLoading(true, 'Comparando archivos...')
      store.clearResult()

      const formData = new FormData()
      formData.append('file_a', fileA)
      formData.append('file_b', fileB)

      const response = await axios.post(`${API_URL}/compare/reconcile`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 0,
      })

      // response.data es JSON con stats + discrepancias
      const data = response.data
      store.setReconciliationResult(data)

      if (data.all_clear) {
        store.setSuccess('✅ Sin incongruencias — Todos los datos coinciden.')
      } else {
        const total = data.stats.campos_diferentes
        store.setSuccess(`⚠️ Se encontraron ${total} inconsistencia(s) en los datos.`)
      }

    } catch (err) {
      console.error('Error al comparar:', err)
      store.setError(_extractErrorMessage(err))
    } finally {
      store.setLoading(false)
    }
  }

  /**
   * Descarga el reporte Excel a partir del report_id.
   */
  const downloadReport = () => {
    const result = store.reconciliationResult
    if (!result || !result.report_id) return

    const url = `${API_URL}/compare/download/${result.report_id}`
    window.open(url, '_blank')
  }

  // === Utilidades privadas ===

  function _downloadBlob(blob, fileName) {
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = fileName
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  }

  function _extractErrorMessage(err) {
    if (err.response) {
      if (err.response.data?.detail) {
        return err.response.data.detail
      }
      return `Error ${err.response.status}: ${err.response.statusText}`
    }
    return err.message || 'Error desconocido al procesar'
  }

  return {
    shuffleExcel,
    reconcileFiles,
    downloadReport,
  }
}
