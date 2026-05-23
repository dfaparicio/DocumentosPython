import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

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
    clearAll
  }
})
