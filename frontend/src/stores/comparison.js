import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useComparisonStore = defineStore('comparison', () => {
  // Archivos a comparar
  const fileA = ref(null)
  const fileB = ref(null)

  // Estado
  const loading = ref(false)
  const loadingMessage = ref('')
  const error = ref('')
  const success = ref('')

  // Resultado de reconciliación (JSON con stats + discrepancias)
  const reconciliationResult = ref(null)



  // Computed
  const hasBothFiles = computed(() => fileA.value !== null && fileB.value !== null)
  const hasFileA = computed(() => fileA.value !== null)
  const hasFileB = computed(() => fileB.value !== null)
  const hasResult = computed(() => reconciliationResult.value !== null)

  // Computed del resultado
  const stats = computed(() => reconciliationResult.value?.stats || null)
  const discrepancies = computed(() => reconciliationResult.value?.discrepancias || [])
  const onlyInA = computed(() => reconciliationResult.value?.solo_en_1_detalle || [])
  const onlyInB = computed(() => reconciliationResult.value?.solo_en_2_detalle || [])
  const allClear = computed(() => reconciliationResult.value?.all_clear ?? true)

  // Actions
  function setFileA(file) {
    fileA.value = file
    error.value = ''
  }

  function setFileB(file) {
    fileB.value = file
    error.value = ''
  }

  function clearFileA() {
    fileA.value = null
  }

  function clearFileB() {
    fileB.value = null
  }

  function setLoading(isLoading, message = '') {
    loading.value = isLoading
    loadingMessage.value = message
  }

  function setError(message) {
    error.value = message
    success.value = ''
  }

  function setSuccess(message) {
    success.value = message
    error.value = ''
  }

  function setReconciliationResult(data) {
    reconciliationResult.value = data
  }



  function clearResult() {
    reconciliationResult.value = null
  }

  function clearAll() {
    fileA.value = null
    fileB.value = null
    loading.value = false
    loadingMessage.value = ''
    error.value = ''
    success.value = ''
    reconciliationResult.value = null
  }

  return {
    fileA,
    fileB,
    loading,
    loadingMessage,
    error,
    success,
    reconciliationResult,
    hasBothFiles,
    hasFileA,
    hasFileB,
    hasResult,
    stats,
    discrepancies,
    onlyInA,
    onlyInB,
    allClear,
    setFileA,
    setFileB,
    clearFileA,
    clearFileB,
    setLoading,
    setError,
    setSuccess,
    setReconciliationResult,
    clearResult,
    clearAll,
  }
})
