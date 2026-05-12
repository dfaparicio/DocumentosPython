import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useExtractionStore = defineStore('extraction', () => {
  const selectedFile = ref(null)
  const loading = ref(false)
  const errorMessage = ref('')
  const successMessage = ref('')
  const excelFile = ref(null)
  const excelFileName = ref('')

  const hasFile = computed(() => selectedFile.value !== null)
  const hasError = computed(() => errorMessage.value !== '')

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

  function clearAll() {
    clearFile()
    clearMessages()
    clearExcel()
  }

  return {
    selectedFile,
    loading,
    errorMessage,
    successMessage,
    excelFile,
    excelFileName,
    hasFile,
    hasError,
    setFile,
    clearFile,
    setLoading,
    setError,
    setSuccess,
    clearMessages,
    setExcelFile,
    clearExcel,
    clearAll
  }
})
