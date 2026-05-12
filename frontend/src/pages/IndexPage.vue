<!--
  Página principal de la aplicación
  Aquí se integra todo: subida de archivo, procesamiento y descarga
-->
<template>
  <div class="index-page">
    <!-- Sección de bienvenida -->
    <q-card class="q-mb-lg card-shadow">
      <q-card-section class="bg-gradient-primary text-white">
        <div class="row items-center">
          <div class="col-12 col-md-8">
            <h1 class="text-h4 text-weight-bold q-mb-sm">
              Extrae datos de cédulas con IA
            </h1>
            <p class="text-body1">
              Sube un PDF con las fotocopias de las cédulas y obtén un Excel
              con los nombres, apellidos, número de documento y fecha de nacimiento
              automáticamente.
            </p>
          </div>
          <div class="col-12 col-md-4 text-center">
            <q-icon name="auto_awesome" size="100px" class="q-ma-md" />
          </div>
        </div>
      </q-card-section>
    </q-card>

    <!-- Sección principal -->
    <div class="row q-col-gutter-lg">
      <!-- Columna izquierda: Subida de archivo -->
      <div class="col-12 col-md-5">
        <!-- Componente para subir PDF -->
        <FileUpload
          ref="fileUploadRef"
          title="Sube tu PDF aquí"
          @file-selected="onFileSelected"
          @file-removed="onFileRemoved"
        />

        <!-- Botón para procesar el archivo -->
        <q-btn
          v-if="store.hasFile"
          color="primary"
          size="lg"
          rounded
          class="full-width action-button q-mt-md"
          :loading="store.loading"
          :disable="store.loading"
          @click="processFile"
        >
          <q-icon left name="smart_toy" />
          {{ store.loading ? 'Procesando...' : 'Extraer Datos' }}
        </q-btn>

        <!-- Botón para procesar nuevo archivo -->
        <q-btn
          v-if="!store.hasFile && store.excelFile"
          color="accent"
          size="lg"
          rounded
          class="full-width action-button q-mt-md"
          @click="processNewFile"
        >
          <q-icon left name="add_circle" />
          Procesar Nuevo Archivo
        </q-btn>
      </div>

      <!-- Columna derecha: Tabla de datos -->
      <div class="col-12 col-md-7">
        <!-- Componente de tabla de datos -->
        <DataTable
          v-if="store.excelFile"
          :data="[]"
          @clear-all="onClearAll"
        />

        <!-- Mensaje de éxito cuando hay archivo Excel -->
        <q-card v-if="store.excelFile && !store.loading" class="q-mb-lg card-shadow">
          <q-card-section class="bg-positive text-white q-pa-md">
            <div class="row items-center">
              <q-icon name="check_circle" size="32px" class="q-mr-md" />
              <div>
                <div class="text-h6">¡Excel generado correctamente!</div>
                <div class="text-body2">Tu archivo está listo para descargar</div>
              </div>
            </div>
          </q-card-section>
        </q-card>

        <!-- Botón para descargar Excel -->
        <q-btn
          v-if="store.excelFile && !store.loading"
          color="secondary"
          size="lg"
          rounded
          class="full-width action-button q-mb-md"
          @click="downloadExcel"
        >
          <q-icon left name="download" />
          Descargar Excel
        </q-btn>

        <!-- Mensaje inicial cuando no hay archivo -->
        <q-card v-if="!store.excelFile && !store.hasFile" class="card-shadow">
          <q-card-section class="q-pa-xl text-center">
            <q-icon
              name="upload_file"
              size="80px"
              color="grey-4"
              class="q-mb-md"
            />
            <div class="text-h6 text-grey-6 q-mb-sm">
              Comienza subiendo un PDF
            </div>
            <div class="text-body2 text-grey-5">
              Arrastra tu archivo o haz clic en el área de subida para comenzar
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Mensajes de estado -->
    <q-banner
      v-if="store.errorMessage"
      class="bg-negative text-white q-mt-lg"
      rounded
    >
      <template v-slot:avatar>
        <q-icon name="error" />
      </template>
      {{ store.errorMessage }}
    </q-banner>

    <q-banner
      v-if="store.successMessage && !store.excelFile"
      class="bg-positive text-white q-mt-lg"
      rounded
    >
      <template v-slot:avatar>
        <q-icon name="check_circle" />
      </template>
      {{ store.successMessage }}
    </q-banner>

    <!-- Overlay de carga -->
    <div v-if="store.loading" class="loading-overlay">
      <div class="text-center">
        <q-spinner-puff
          color="primary"
          size="100px"
          class="q-mb-md"
        />
        <div class="text-h5 text-grey-8 q-mb-md">
          Procesando PDF...
        </div>
        <div class="text-body1 text-grey-6">
          Esto puede tardar unos segundos dependiendo del tamaño del archivo
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useExtractionStore } from '../stores/extraction'
import { useExtraction } from '../composables/useExtraction'
import FileUpload from '../components/FileUpload.vue'
import DataTable from '../components/DataTable.vue'
import { Notify } from 'quasar'

// Usamos el store y el composable
const store = useExtractionStore()
const { extractFromPdf, downloadExcel } = useExtraction()

// Referencia al componente FileUpload
const fileUploadRef = ref(null)

/**
 * Se ejecuta cuando el usuario selecciona un archivo
 */
function onFileSelected(file) {
  store.setFile(file)

  Notify.create({
    type: 'info',
    message: 'Archivo seleccionado correctamente',
    caption: 'Haz clic en "Extraer Datos" para comenzar el proceso',
    position: 'top',
    timeout: 3000,
    icon: 'info'
  })
}

/**
 * Se ejecuta cuando el usuario elimina el archivo seleccionado
 */
function onFileRemoved() {
  store.clearFile()
}

/**
 * Procesa el archivo PDF seleccionado
 */
async function processFile() {
  if (!store.selectedFile) {
    Notify.create({
      type: 'warning',
      message: 'Por favor selecciona un archivo PDF primero',
      position: 'top',
      icon: 'warning'
    })
    return
  }

  try {
    await extractFromPdf(store.selectedFile)
  } catch (error) {
    console.error('Error al procesar archivo:', error)
  }
}

/**
 * Procesa un nuevo archivo (limpia el estado anterior)
 */
function processNewFile() {
  store.clearAll()

  Notify.create({
    type: 'info',
    message: 'Listo para un nuevo archivo',
    caption: 'Sube un nuevo PDF para comenzar',
    position: 'top',
    timeout: 2000,
    icon: 'info'
  })
}

/**
 * Limpia todos los datos y reinicia la aplicación
 */
function onClearAll() {
  store.clearAll()

  Notify.create({
    type: 'info',
    message: 'Datos limpiados correctamente',
    position: 'top',
    timeout: 2000,
    icon: 'delete_sweep'
  })
}
</script>

<style scoped>
.index-page {
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.bg-gradient-primary {
  background: linear-gradient(135deg, #2E7D32 0%, #4CAF50 100%);
}

.action-button {
  min-width: 150px;
  height: 50px;
  font-size: 16px;
  font-weight: 500;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.action-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 15px rgba(0, 0, 0, 0.2);
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.95);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

@media (max-width: 768px) {
  .action-button {
    width: 100%;
    min-width: unset;
  }
}
</style>
