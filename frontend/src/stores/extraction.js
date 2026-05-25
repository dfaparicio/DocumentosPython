import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const useExtractionStore = defineStore('extraction', () => {
  const selectedFile = ref(null)
  const loading = ref(false)
  const errorMessage = ref('')
  const successMessage = ref('')
  const excelFile = ref(null)
  const excelFileName = ref('')

  // Progreso del procesamiento
  const progress = ref({
    status: 'idle',
    total_pages: 0,
    processed_pages: 0,
    current_page: 0,
    documents_found: 0,
    errors: 0,
    percentage: 0
  })

  // API Key state
  const apiKeyConfigured = ref(false)
  const apiKeyMasked = ref('')
  const apiKeyLoading = ref(false)

  const hasFile = computed(() => selectedFile.value !== null)
  const hasError = computed(() => errorMessage.value !== '')
  const isProcessing = computed(() => loading.value && progress.value.status === 'processing')

  function setFile(file) {
    selectedFile.value = file
    errorMessage.value = ''
  }

  function clearFile() {
    selectedFile.value = null
  }

  function setLoading(isLoading) {
    loading.value = isLoading
  }

  function setError(message) {
    errorMessage.value = message
    successMessage.value = ''
  }

  function setSuccess(message) {
    successMessage.value = message
    errorMessage.value = ''
  }

  function clearMessages() {
    errorMessage.value = ''
    successMessage.value = ''
  }

  function setExcelFile(file, fileName) {
    excelFile.value = file
    excelFileName.value = fileName
  }

  function clearExcel() {
    excelFile.value = null
    excelFileName.value = ''
  }

  function setProgress(data) {
    progress.value = { ...data }
  }

  function resetProgress() {
    progress.value = {
      status: 'idle',
      total_pages: 0,
      processed_pages: 0,
      current_page: 0,
      documents_found: 0,
      errors: 0,
      percentage: 0
    }
  }

  function clearAll() {
    clearFile()
    clearMessages()
    clearExcel()
    resetProgress()
  }

  // API Key actions
  async function fetchApiKeyStatus() {
    try {
      apiKeyLoading.value = true
      const response = await axios.get(`${API_URL}/api/config/api-key`)
      apiKeyConfigured.value = response.data.configured
      apiKeyMasked.value = response.data.masked || ''
    } catch (error) {
      console.error('Error al obtener estado de API key:', error)
      apiKeyConfigured.value = false
      apiKeyMasked.value = ''
    } finally {
      apiKeyLoading.value = false
    }
  }

  async function saveApiKey(key) {
    try {
      apiKeyLoading.value = true
      await axios.put(`${API_URL}/api/config/api-key`, { api_key: key })
      await fetchApiKeyStatus()
      return true
    } catch (error) {
      const detail = error.response?.data?.detail || 'Error al guardar la API key'
      throw new Error(detail)
    } finally {
      apiKeyLoading.value = false
    }
  }

  async function deleteApiKey() {
    try {
      apiKeyLoading.value = true
      await axios.delete(`${API_URL}/api/config/api-key`)
      apiKeyConfigured.value = false
      apiKeyMasked.value = ''
      return true
    } catch (error) {
      const detail = error.response?.data?.detail || 'Error al eliminar la API key'
      throw new Error(detail)
    } finally {
      apiKeyLoading.value = false
    }
  }

  return {
    selectedFile,
    loading,
    errorMessage,
    successMessage,
    excelFile,
    excelFileName,
    progress,
    hasFile,
    hasError,
    isProcessing,
    apiKeyConfigured,
    apiKeyMasked,
    apiKeyLoading,
    setFile,
    clearFile,
    setLoading,
    setError,
    setSuccess,
    clearMessages,
    setExcelFile,
    clearExcel,
    setProgress,
    resetProgress,
    clearAll,
    fetchApiKeyStatus,
    saveApiKey,
    deleteApiKey
  }
})
