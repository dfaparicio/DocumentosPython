<template>
  <div class="home">
    <div class="container">
      <!-- Header -->
      <header class="header">
        <h1 class="title">
          <span class="text-gradient">Extrae datos de cédulas con IA</span>
        </h1>
        <p class="subtitle">
          Sube un PDF con las fotocopias de las cédulas y obtén un Excel con los datos automáticamente.
        </p>
      </header>

      <!-- Main Content -->
      <div class="main-content">
        <!-- Left Column: Upload -->
        <div class="column left-column">
          <div class="card upload-card">
            <h2 class="card-title">Sube tu PDF aquí</h2>

            <!-- Drop Zone -->
            <div
              class="drop-zone"
              :class="{ dragging: isDragging }"
              @dragover.prevent="onDragOver"
              @dragleave.prevent="onDragLeave"
              @drop.prevent="onDrop"
              @click="selectFile"
            >
              <svg class="upload-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.935 6h4a5 5 0 011.897-1.903A4 4 0 0121 16V7a4 4 0 00-4-4H7zm3 4V6h3v4h-3z"/>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8h2a2 2 0 012 2v9"/>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15l3 3"/>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 12l3-3"/>
              </svg>

              <p class="upload-text">
                Arrastra un PDF aquí o haz clic para seleccionar
              </p>

              <input
                ref="fileInput"
                type="file"
                accept=".pdf"
                class="hidden-input"
                @change="onFileSelected"
              />

              <p v-if="errorMessage" class="error-text">
                {{ errorMessage }}
              </p>
            </div>

            <!-- Selected File Preview -->
            <div v-if="selectedFile" class="file-preview">
              <svg class="pdf-icon" viewBox="0 0 24 24" fill="currentColor">
                <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6z"/>
                <path d="M14 2v6h6"/>
                <path d="M16 13H8"/>
                <path d="M16 17H8"/>
                <path d="M10 9H8"/>
              </svg>

              <div class="file-info">
                <div class="file-name">{{ selectedFile.name }}</div>
                <div class="file-size">{{ formatFileSize(selectedFile.size) }}</div>
              </div>

              <button class="clear-btn" @click="removeFile">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                </svg>
              </button>
            </div>

            <!-- Process Button -->
            <button
              v-if="selectedFile"
              class="btn btn-primary process-btn"
              :disabled="loading"
              @click="processFile"
            >
              <svg v-if="!loading" class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1m-4 0v1m0-1H3"/>
              </svg>
              <span v-if="!loading">Extraer Datos</span>
              <span v-else>Procesando...</span>
            </button>

            <!-- New File Button -->
            <button
              v-if="!selectedFile && excelFile"
              class="btn btn-primary"
              @click="processNewFile"
            >
              <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
              </svg>
              Procesar Nuevo Archivo
            </button>
          </div>
        </div>

        <!-- Right Column: Results -->
        <div class="column right-column">
          <!-- Success Card -->
          <div v-if="excelFile && !loading" class="card success-card">
            <svg class="success-icon" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 22C6.477 22 2 17.523 2 12S6.477 2 12 2s-5 3.478-5 10c0 5.523 4.477 10 10s10-4.477 10-10S17.523 2 12 2zm-1.177-7.86l-2.765 2.247 6.223 5.012 1.384-3.168L5.863 8.65 7.236-5.012 1.177 3.857-.233 4.005-1.177 7.86z"/>
            </svg>

            <div class="success-content">
              <h3 class="success-title">¡Excel generado correctamente!</h3>
              <p class="success-message">Tu archivo está listo para descargar</p>
            </div>
          </div>

          <!-- Download Button -->
          <button
            v-if="excelFile && !loading"
            class="btn btn-primary download-btn"
            @click="downloadExcel"
          >
            <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 10l5 5 5-5"/>
            </svg>
            Descargar Excel
          </button>

          <!-- Initial Card -->
          <div v-if="!excelFile && !selectedFile" class="card initial-card">
            <svg class="initial-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 13h6m-3-3v6m5 6v-6m2 0h-7"/>
            </svg>

            <h3 class="initial-title">Comienza subiendo un PDF</h3>
            <p class="initial-message">Arrastra tu archivo o haz clic en el área de subida para comenzar</p>
          </div>
        </div>
      </div>

      <!-- Status Messages -->
      <div v-if="errorMessage" class="alert alert-error">
        {{ errorMessage }}
      </div>

      <div v-if="successMessage && !excelFile" class="alert alert-success">
        {{ successMessage }}
      </div>
    </div>

    <!-- Loading Overlay -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-content">
        <div class="spinner"></div>
        <p class="loading-text">Procesando PDF...</p>
        <p class="loading-subtext">Esto puede tardar unos segundos</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useExtractionStore } from '../stores/extraction'
import { useExtraction } from '../composables/useExtraction'

const store = useExtractionStore()
const { extractFromPdf, downloadExcel } = useExtraction()

const isDragging = ref(false)
const errorMessage = ref('')
const fileInput = ref(null)

const selectedFile = computed(() => store.selectedFile)
const loading = computed(() => store.loading)
const excelFile = computed(() => store.excelFile)
const successMessage = computed(() => store.successMessage)

function onDragOver() {
  isDragging.value = true
}

function onDragLeave() {
  isDragging.value = false
}

function onDrop(event) {
  isDragging.value = false
  const file = event.dataTransfer.files[0]
  handleFile(file)
}

function selectFile() {
  fileInput.value.click()
}

function onFileSelected(event) {
  const file = event.target.files[0]
  handleFile(file)
  event.target.value = ''
}

function handleFile(file) {
  if (!file) return

  if (file.type !== 'application/pdf' && !file.name.endsWith('.pdf')) {
    errorMessage.value = 'Por favor selecciona un archivo PDF'
    alert('Solo se permiten archivos PDF')
    return
  }


  store.setFile(file)
  errorMessage.value = ''
}

function removeFile() {
  store.clearFile()
  errorMessage.value = ''
}

async function processFile() {
  if (!store.selectedFile) {
    alert('Por favor selecciona un archivo PDF primero')
    return
  }

  try {
    await extractFromPdf(store.selectedFile)
  } catch (error) {
    console.error('Error al procesar archivo:', error)
  }
}

function processNewFile() {
  store.clearAll()
}

function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
}
</script>

<style scoped>
.home {
  min-height: 100vh;
}

.header {
  text-align: center;
  margin-bottom: 40px;
}

.title {
  font-size: 36px;
  font-weight: 700;
  margin-bottom: 16px;
  color: var(--gray-800);
}

.subtitle {
  font-size: 18px;
  color: var(--gray-600);
  max-width: 700px;
  margin: 0 auto;
  line-height: 1.6;
}

.main-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 40px;
}

.column {
  display: flex;
  flex-direction: column;
}

.upload-card {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.card-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--gray-800);
  margin-bottom: 16px;
}

.upload-icon {
  width: 80px;
  height: 80px;
  color: var(--gray-400);
  margin-bottom: 16px;
}

.upload-text {
  font-size: 16px;
  color: var(--gray-600);
  margin-bottom: 12px;
}

.hidden-input {
  display: none;
}

.error-text {
  color: var(--error);
  font-size: 14px;
  margin-top: 12px;
}

.file-preview {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--gray-50);
  border-radius: 8px;
}

.pdf-icon {
  width: 32px;
  height: 32px;
  color: var(--error);
}

.file-info {
  flex: 1;
}

.file-name {
  font-weight: 500;
  color: var(--gray-800);
  margin-bottom: 4px;
}

.file-size {
  font-size: 14px;
  color: var(--gray-500);
}

.clear-btn {
  background: var(--gray-200);
  border: none;
  padding: 8px;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.clear-btn:hover {
  background: var(--gray-300);
}

.clear-btn svg {
  width: 16px;
  height: 16px;
  color: var(--error);
}

.process-btn {
  width: 100%;
  justify-content: center;
  font-size: 18px;
  padding: 16px;
}

.btn-icon {
  width: 20px;
  height: 20px;
}

.success-card,
.initial-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 40px;
}

.success-icon {
  width: 80px;
  height: 80px;
  color: var(--success);
  margin-bottom: 16px;
}

.success-content {
  width: 100%;
}

.success-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--success);
  margin-bottom: 8px;
}

.success-message {
  font-size: 16px;
  color: var(--gray-600);
}

.initial-icon {
  width: 80px;
  height: 80px;
  color: var(--gray-400);
  margin-bottom: 16px;
}

.initial-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--gray-700);
  margin-bottom: 8px;
}

.initial-message {
  font-size: 16px;
  color: var(--gray-600);
}

.download-btn {
  width: 100%;
  justify-content: center;
  font-size: 18px;
  padding: 16px;
  margin-top: 20px;
}

.loading-content {
  text-align: center;
}

.spinner {
  margin-bottom: 24px;
}

.loading-text {
  font-size: 24px;
  font-weight: 600;
  color: var(--gray-800);
  margin-bottom: 8px;
}

.loading-subtext {
  font-size: 16px;
  color: var(--gray-600);
}

@media (max-width: 768px) {
  .main-content {
    grid-template-columns: 1fr;
  }

  .title {
    font-size: 28px;
  }

  .subtitle {
    font-size: 16px;
  }

  .success-card,
  .initial-card {
    padding: 24px;
  }
}
</style>
