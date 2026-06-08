import axios from 'axios'
import { useComparisonStore } from '../stores/comparison'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export function useComparison() {
  const store = useComparisonStore()

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
        store.setSuccess('✅ Ambos archivos contienen exactamente las mismas cédulas.')
      } else {
        const soloEn1 = data.stats.solo_en_1 || 0
        const soloEn2 = data.stats.solo_en_2 || 0
        const total = soloEn1 + soloEn2
        store.setSuccess(`⚠️ ${total} cédula(s) no coinciden entre los archivos.`)
      }

    } catch (err) {
      console.error('Error al comparar:', err)
      store.setError(_extractErrorMessage(err))
    } finally {
      store.setLoading(false)
    }
  }

  // === Utilidades privadas ===

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
    reconcileFiles,
  }
}
