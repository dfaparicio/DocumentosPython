<template>
  <div class="home">
    <div class="container">
      <!-- Header -->
      <header class="header">
        <h1 class="title">
          <span class="text-gradient">Extrae datos de cédulas  en segundos</span>
        </h1>
        <p class="subtitle">
          Sube un PDF con las fotocopias de las cédulas y obtén un Excel con los datos automáticamente.
        </p>
      </header>

      <!-- Main Content -->
      <div class="main-content" :class="{ 'has-results': excelFile && !loading }">
        <!-- Upload Column (centered when alone, left when results exist) -->
        <div class="column upload-column">
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
  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 16V4m0 0L8 8m4-4l4 4"/>
  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 16v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2"/>
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

        <!-- Right Column: Results (solo visible cuando hay resultados) -->
        <div v-if="excelFile && !loading" class="column right-column">
          <!-- Success Card with Results -->
          <div v-if="excelFile && !loading" class="card success-card">
            <svg class="success-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
            </svg>

            <div class="success-content">
              <h3 class="success-title">¡Excel generado correctamente!</h3>
              <p class="success-message">{{ successMessage }}</p>

              <!-- Results Summary -->
              <div v-if="progress.total_pages > 0" class="results-summary">
                <div class="result-item">
                  <span class="result-number">{{ progress.documents_found || '—' }}</span>
                  <span class="result-label">Documentos</span>
                </div>
                <div class="result-item">
                  <span class="result-number">{{ progress.total_pages }}</span>
                  <span class="result-label">Páginas</span>
                </div>
                <div v-if="progress.errors > 0" class="result-item result-error">
                  <span class="result-number">{{ progress.errors }}</span>
                  <span class="result-label">Errores</span>
                </div>
              </div>

              <p v-if="progress.errors > 0" class="review-notice">
                ⚠️ Revisa la hoja <strong>"Revisión Requerida"</strong> en el Excel para ver las páginas con problemas.
              </p>
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
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15V3"/>
            </svg>
            Descargar Excel
          </button>

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

    <!-- Loading Overlay with LIVE Progress -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-content">
        <div class="spinner"></div>

        <!-- Progress Info -->
        <div v-if="progress.status === 'converting'" class="progress-section">
          <p class="loading-text">📄 Convirtiendo PDF a imágenes...</p>
          <p class="loading-subtext">Preparando las páginas para el análisis</p>
        </div>

        <div v-else-if="progress.status === 'processing'" class="progress-section">
          <p class="loading-text">🤖 Analizando documentos con IA...</p>

          <!-- Progress Bar -->
          <div class="progress-bar-container">
            <div class="progress-bar" :style="{ width: progress.percentage + '%' }"></div>
          </div>

          <p class="progress-percentage">{{ Math.round(progress.percentage) }}%</p>

          <!-- Stats -->
          <div class="progress-stats">
            <div class="stat">
              <span class="stat-value">{{ progress.processed_pages }}</span>
              <span class="stat-label">de {{ progress.total_pages }} páginas</span>
            </div>
            <div v-if="progress.documents_found > 0" class="stat">
              <span class="stat-value">{{ progress.documents_found }}</span>
              <span class="stat-label">documentos</span>
            </div>
            <div v-if="progress.errors > 0" class="stat stat-error">
              <span class="stat-value">{{ progress.errors }}</span>
              <span class="stat-label">errores</span>
            </div>
          </div>

          <p class="loading-subtext">
            Procesando página {{ progress.current_page }} de {{ progress.total_pages }}
          </p>
        </div>

        <div v-else class="progress-section">
          <p class="loading-text">Procesando PDF...</p>
          <p class="loading-subtext">Esto puede tardar unos segundos</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
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
const progress = computed(() => store.progress)

onMounted(() => {
  store.fetchApiKeyStatus()
})

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

/* Main Content */
.main-content {
  display: flex;
  justify-content: center;
  gap: 24px;
  margin-bottom: 40px;
}

.main-content.has-results {
  display: grid;
  grid-template-columns: 1fr 1fr;
}

.upload-column {
  max-width: 600px;
  width: 100%;
}

.main-content.has-results .upload-column {
  max-width: none;
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
  .main-content.has-results {
    grid-template-columns: 1fr;
  }

  .upload-column {
    max-width: none;
  }

  .title {
    font-size: 28px;
  }

  .subtitle {
    font-size: 16px;
  }

  .success-card {
    padding: 24px;
  }
}

/* Progress Bar */
.progress-section {
  width: 100%;
  max-width: 400px;
  margin: 0 auto;
}

.progress-bar-container {
  width: 100%;
  height: 12px;
  background: var(--gray-200);
  border-radius: 6px;
  overflow: hidden;
  margin: 16px 0 8px;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #4f46e5, #7c3aed);
  border-radius: 6px;
  transition: width 0.5s ease;
  min-width: 2%;
}

.progress-percentage {
  font-size: 32px;
  font-weight: 700;
  color: var(--gray-800);
  margin: 8px 0 16px;
}

.progress-stats {
  display: flex;
  justify-content: center;
  gap: 24px;
  margin-bottom: 16px;
}

.stat {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--gray-800);
}

.stat-label {
  font-size: 13px;
  color: var(--gray-500);
  margin-top: 2px;
}

.stat-error .stat-value {
  color: #ef4444;
}

.stat-error .stat-label {
  color: #ef4444;
}

/* Results Summary */
.results-summary {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin: 20px 0;
  padding: 16px;
  background: var(--gray-50);
  border-radius: 12px;
}

.result-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 16px;
}

.result-number {
  font-size: 28px;
  font-weight: 700;
  color: #4f46e5;
}

.result-label {
  font-size: 13px;
  color: var(--gray-500);
  margin-top: 4px;
}

.result-error .result-number {
  color: #ef4444;
}

.review-notice {
  margin-top: 16px;
  padding: 12px 16px;
  background: #fef3c7;
  border: 1px solid #f59e0b;
  border-radius: 8px;
  font-size: 14px;
  color: #92400e;
  text-align: left;
}
</style>
