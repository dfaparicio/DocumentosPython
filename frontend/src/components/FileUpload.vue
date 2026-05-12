<!--
  Componente para subir archivos PDF
  Permite arrastrar y soltar archivos, o seleccionarlos con el explorador
-->
<template>
  <div class="file-upload">
    <!-- Área para arrastrar y soltar archivos -->
    <div
      class="drop-zone q-pa-xl"
      :class="{ 'dragging': isDragging }"
      @dragover.prevent="onDragOver"
      @dragleave.prevent="onDragLeave"
      @drop.prevent="onDrop"
      @click="selectFile"
    >
      <!-- Icono principal -->
      <q-icon
        :name="isDragging ? 'cloud_upload' : 'upload_file'"
        :size="isDragging ? '120px' : '100px'"
        :color="isDragging ? 'primary' : 'grey-5'"
        class="q-mb-md"
      />

      <!-- Título del componente -->
      <div class="text-h6 text-grey-9 q-mb-sm">
        {{ title }}
      </div>

      <!-- Mensaje de instrucción -->
      <div class="text-body1 text-grey-7 q-mb-md">
        Arrastra un PDF aquí o haz clic para seleccionar
      </div>

      <!-- Mensaje de error si lo hay -->
      <div v-if="errorMessage" class="text-negative q-mt-md">
        <q-icon name="error" class="q-mr-xs" />
        {{ errorMessage }}
      </div>
    </div>

    <!-- Input de archivo oculto (para el clic) -->
    <input
      ref="fileInput"
      type="file"
      accept=".pdf"
      class="hidden"
      @change="onFileSelected"
    />

    <!-- Vista previa del archivo seleccionado -->
    <q-card v-if="selectedFile" class="q-mt-md card-shadow">
      <q-card-section>
        <div class="row items-center">
          <!-- Icono de archivo -->
          <div class="col-auto q-mr-md">
            <q-icon name="picture_as_pdf" size="48px" color="primary" />
          </div>

          <!-- Nombre y tamaño del archivo -->
          <div class="col">
            <div class="text-subtitle1 text-grey-9">
              {{ selectedFile.name }}
            </div>
            <div class="text-caption text-grey-6">
              {{ formatFileSize(selectedFile.size) }}
            </div>
          </div>

          <!-- Botón para eliminar el archivo -->
          <div class="col-auto">
            <q-btn
              round
              flat
              dense
              icon="close"
              color="negative"
              @click="removeFile"
            />
          </div>
        </div>
      </q-card-section>
    </q-card>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { Notify } from 'quasar'

// Props que recibe el componente
const props = defineProps({
  // Título del componente
  title: {
    type: String,
    default: 'Subir PDF de cédulas'
  }
})

// Emits para comunicarse con el componente padre
const emit = defineEmits(['file-selected', 'file-removed'])

// Variables reactivas
const isDragging = ref(false)
const selectedFile = ref(null)
const errorMessage = ref('')
const fileInput = ref(null)

/**
 * Maneja el evento de arrastrar un archivo sobre el área
 */
function onDragOver() {
  isDragging.value = true
}

/**
 * Maneja el evento de salir del área con el archivo
 */
function onDragLeave() {
  isDragging.value = false
}

/**
 * Maneja el evento de soltar un archivo en el área
 */
function onDrop(event) {
  isDragging.value = false

  // Obtenemos el archivo que se soltó
  const file = event.dataTransfer.files[0]

  // Procesamos el archivo
  handleFile(file)
}

/**
 * Abre el explorador de archivos para seleccionar uno
 */
function selectFile() {
  fileInput.value.click()
}

/**
 * Maneja la selección de archivo desde el explorador
 */
function onFileSelected(event) {
  const file = event.target.files[0]
  handleFile(file)

  // Limpiamos el input para que el mismo archivo pueda seleccionarse de nuevo
  event.target.value = ''
}

/**
 * Procesa el archivo seleccionado
 */
function handleFile(file) {
  // Verificamos que sea un archivo
  if (!file) {
    return
  }

  // Verificamos que sea un PDF
  if (file.type !== 'application/pdf' && !file.name.endsWith('.pdf')) {
    errorMessage.value = 'Por favor selecciona un archivo PDF'
    Notify.create({
      type: 'warning',
      message: 'Solo se permiten archivos PDF',
      position: 'top',
      icon: 'warning'
    })
    return
  }


  // Si todo está bien, guardamos el archivo
  selectedFile.value = file
  errorMessage.value = ''

  // Emitimos el evento al componente padre
  emit('file-selected', file)

  // Mostramos notificación de éxito
  Notify.create({
    type: 'positive',
    message: 'Archivo PDF seleccionado correctamente',
    position: 'top',
    timeout: 2000,
    icon: 'check'
  })
}

/**
 * Elimina el archivo seleccionado
 */
function removeFile() {
  selectedFile.value = null
  errorMessage.value = ''

  // Emitimos el evento al componente padre
  emit('file-removed')

  // Mostramos notificación
  Notify.create({
    type: 'info',
    message: 'Archivo eliminado',
    position: 'top',
    timeout: 1500,
    icon: 'delete'
  })
}

/**
 * Formatea el tamaño del archivo en formato legible
 */
function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes'

  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
}

/**
 * Exponemos el archivo seleccionado para que el componente padre pueda acceder
 */
defineExpose({
  selectedFile
})
</script>

<style scoped>
.file-upload {
  width: 100%;
}

.drop-zone {
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px dashed #bdbdbd;
  border-radius: 12px;
  background-color: white;
}

.drop-zone:hover {
  border-color: #4CAF50;
  background-color: rgba(76, 175, 80, 0.05);
}

.drop-zone.dragging {
  border-color: #2E7D32;
  background-color: rgba(46, 125, 50, 0.1);
  transform: scale(1.02);
}

.hidden {
  display: none;
}

@media (max-width: 768px) {
  .drop-zone {
    padding: 30px 15px;
  }
}
</style>
