import axios from 'axios'
import { useExtractionStore } from '../stores/extraction'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export function useExtraction() {
  const store = useExtractionStore()

  const extractFromPdf = async (file) => {
    try {
      store.setLoading(true)
      store.clearMessages()

      const formData = new FormData()
      formData.append('pdf_file', file)

      const response = await axios.post(`${API_URL}/extract/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        responseType: 'blob'
      })

      const excelFile = response.data

      const now = new Date()
      const dateStr = now.toISOString().split('T')[0]
      const timeStr = now.toTimeString().split(' ')[0].replace(/:/g, '-')
      const fileName = `cedulas_extraidas_${dateStr}_${timeStr}.xlsx`

      store.setExcelFile(excelFile, fileName)
      store.setSuccess('PDF procesado correctamente')

    } catch (error) {
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
      } else if (error.message) {
        errorMessage = error.message
      }

      store.setError(errorMessage)
    } finally {
      store.setLoading(false)
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
      alert('Excel descargado correctamente')
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
