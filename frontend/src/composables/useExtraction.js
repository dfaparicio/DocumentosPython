import axios from 'axios'
import { useExtractionStore } from '../stores/extraction'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export function useExtraction() {
  const store = useExtractionStore()
  let progressInterval = null

  /**
   * Inicia el polling de progreso cada 800ms
   */
  const startProgressPolling = () => {
    stopProgressPolling()
    progressInterval = setInterval(async () => {
      try {
        const response = await axios.get(`${API_URL}/extract/progress`)
        store.setProgress(response.data)

        // Auto-detener cuando termine
        if (response.data.status === 'done' || response.data.status === 'error') {
          stopProgressPolling()
        }
      } catch (error) {
        // Silenciar errores de polling
      }
    }, 1000)
  }

  /**
   * Detiene el polling de progreso
   */
  const stopProgressPolling = () => {
    if (progressInterval) {
      clearInterval(progressInterval)
      progressInterval = null
    }
  }

  /**
   * Envía el PDF al backend y espera el Excel de resultado.
   * Mientras tanto, hace polling del progreso.
   */
  const extractFromPdf = async (file) => {
    try {
      store.setLoading(true)
      store.clearMessages()
      store.resetProgress()

      // Iniciamos el polling de progreso
      startProgressPolling()

      const formData = new FormData()
      formData.append('pdf_file', file)

      const response = await axios.post(`${API_URL}/extract/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        responseType: 'blob',
        timeout: 0 // Sin timeout — el proceso puede tardar varios minutos
      })

      // Detener polling
      stopProgressPolling()

      // Obtener el progreso final
      try {
        const finalProgress = await axios.get(`${API_URL}/extract/progress`)
        store.setProgress(finalProgress.data)
      } catch (e) {
        // No pasa nada
      }

      const excelFile = response.data

      const now = new Date()
      const dateStr = now.toISOString().split('T')[0]
      const timeStr = now.toTimeString().split(' ')[0].replace(/:/g, '-')
      const fileName = `cedulas_extraidas_${dateStr}_${timeStr}.xlsx`

      store.setExcelFile(excelFile, fileName)

      // Mensaje con estadísticas
      const p = store.progress
      let successMsg = `✅ PDF procesado — ${p.documents_found} documentos extraídos`
      if (p.errors > 0) {
        successMsg += ` (${p.errors} páginas con error)`
      }
      store.setSuccess(successMsg)

    } catch (error) {
      stopProgressPolling()
      console.error('Error al procesar PDF:', error)

      let errorMessage = 'Ocurrió un error al procesar el archivo.'

      if (error.response) {
        if (error.response.data instanceof Blob) {
          try {
            const text = await error.response.data.text()
            errorMessage = text || errorMessage
          } catch (e) {
            // Use default message
          }
        } else if (error.response.data && error.response.data.detail) {
          errorMessage = error.response.data.detail
        }
      } else if (error.code === 'ECONNABORTED') {
        errorMessage = 'El procesamiento tardó demasiado. Intenta con un PDF más pequeño.'
      } else if (error.message) {
        errorMessage = error.message
      }

      store.setError(errorMessage)
    } finally {
      store.setLoading(false)
      stopProgressPolling()
    }
  }

  const downloadExcel = () => {
    if (!store.excelFile) {
      alert('No hay archivo Excel para descargar')
      return
    }

    try {
      const url = window.URL.createObjectURL(store.excelFile)
      const link = document.createElement('a')
      link.href = url
      link.download = store.excelFileName || 'cedulas_extraidas.xlsx'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Error al descargar Excel:', error)
      alert('Error al descargar el Excel')
    }
  }

  return {
    extractFromPdf,
    downloadExcel
  }
}
