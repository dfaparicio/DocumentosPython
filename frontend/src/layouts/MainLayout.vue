<!--
  Layout principal de la aplicación
  Contiene el header, el contenido principal y el footer
-->
<template>
  <q-layout view="hHh lpR fFf">
    <!-- Header de la aplicación -->
    <q-header class="bg-primary text-white">
      <!-- Toolbar principal -->
      <q-toolbar class="q-py-sm">
        <!-- Icono y título de la aplicación -->
        <q-toolbar-title>
          <div class="row items-center no-wrap">
            <q-icon
              name="description_scanner"
              size="32px"
              class="q-mr-sm"
            />
            <span class="text-h5 text-weight-medium">
              Extractor de Cédulas
            </span>
          </div>
        </q-toolbar-title>

        <!-- Espaciador para separar elementos -->
        <q-space />

        <!-- Links de navegación -->
        <q-btn
          flat
          no-caps
          :to="'/'"
          :class="{ 'nav-active': $route.path === '/' }"
          icon="image_scanner"
          label="Extraer"
          class="q-mr-xs"
        />
        <q-btn
          flat
          no-caps
          to="/comparar"
          :class="{ 'nav-active': $route.path === '/comparar' }"
          icon="compare_arrows"
          label="Comparar"
          class="q-mr-md"
        />

        <!-- Icono de información con tooltip -->
        <q-btn
          flat
          dense
          round
          icon="info"
          @click="showInfo"
        >
          <q-tooltip>Información sobre la aplicación</q-tooltip>
        </q-btn>
      </q-toolbar>

      <!-- Barra de progreso cuando está cargando -->
      <q-linear-progress
        v-if="store.loading"
        indeterminate
        color="accent"
        size="3px"
      />
    </q-header>

    <!-- Contenido principal de la aplicación -->
    <q-page-container class="bg-grey-1">
      <q-page class="q-pa-md">
        <!-- Aquí se renderiza la página actual (IndexPage) -->
        <router-view />
      </q-page>
    </q-page-container>

    <!-- Footer de la aplicación -->
    <q-footer class="bg-white text-grey-7">
      <q-toolbar class="q-py-sm">
        <!-- Información de la versión -->
        <div class="text-caption">
          v1.0.0 | Desarrollado con Vue 3, Quasar y Google Gemini
        </div>

        <!-- Espaciador para separar elementos -->
        <q-space />

        <!-- Enlaces útiles -->
        <div class="row items-center no-wrap">
          <q-btn
            flat
            dense
            no-caps
            icon="github"
            label="GitHub"
            href="#"
            target="_blank"
            class="q-mr-sm"
          />

          <q-btn
            flat
            dense
            no-caps
            icon="help"
            label="Ayuda"
            @click="showHelp"
          />
        </div>
      </q-toolbar>
    </q-footer>

    <!-- Diálogo de información -->
    <q-dialog v-model="infoDialog">
      <q-card class="card-shadow">
        <q-card-section class="bg-primary text-white">
          <div class="text-h6">
            <q-icon name="info" class="q-mr-sm" />
            Acerca de Extractor de Cédulas
          </div>
        </q-card-section>

        <q-card-section class="q-pa-md">
          <p class="text-body1">
            Esta aplicación utiliza Inteligencia Artificial (Google Gemini) para extraer
            automáticamente la información de cédulas de identidad contenida en archivos PDF.
          </p>

          <p class="text-body1 q-mt-md">
            <strong>Datos extraídos:</strong>
          </p>
          <ul>
            <li>Nombres</li>
            <li>Apellidos</li>
            <li>Número de Documento (Cédula)</li>
            <li>Fecha de Nacimiento</li>
          </ul>

          <p class="text-body1 q-mt-md">
            <strong>Tecnologías:</strong>
          </p>
          <p class="text-body2">
            Frontend: Vue 3 + Quasar<br>
            Backend: Python + FastAPI<br>
            IA: Google Gemini 1.5 Flash
          </p>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn
            flat
            label="Cerrar"
            color="primary"
            v-close-popup
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Diálogo de ayuda -->
    <q-dialog v-model="helpDialog">
      <q-card class="card-shadow">
        <q-card-section class="bg-primary text-white">
          <div class="text-h6">
            <q-icon name="help" class="q-mr-sm" />
            ¿Cómo usar la aplicación?
          </div>
        </q-card-section>

        <q-card-section class="q-pa-md">
          <q-timeline color="primary">
            <q-timeline-entry
              subtitle="Paso 1"
              icon="upload_file"
            >
              <div class="text-body1">
                Sube un archivo PDF con las fotocopias de las cédulas.
                Puedes arrastrar y soltar el archivo o hacer clic para seleccionarlo.
              </div>
            </q-timeline-entry>

            <q-timeline-entry
              subtitle="Paso 2"
              icon="smart_toy"
            >
              <div class="text-body1">
                La IA analizará el PDF y extraerá los datos de cada cédula automáticamente.
                Este proceso puede tardar unos segundos dependiendo del tamaño del archivo.
              </div>
            </q-timeline-entry>

            <q-timeline-entry
              subtitle="Paso 3"
              icon="table_chart"
            >
              <div class="text-body1">
                Verifica los datos extraídos en la tabla.
                Si algo está incorrecto, puedes procesar el PDF de nuevo.
              </div>
            </q-timeline-entry>

            <q-timeline-entry
              subtitle="Paso 4"
              icon="download"
            >
              <div class="text-body1">
                Descarga el archivo Excel con todos los datos extraídos.
                El archivo tendrá el nombre con fecha y hora para organizarlo mejor.
              </div>
            </q-timeline-entry>
          </q-timeline>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn
            flat
            label="Cerrar"
            color="primary"
            v-close-popup
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-layout>
</template>

<script setup>
import { ref } from 'vue'
import { useExtractionStore } from '../stores/extraction'

// Usamos el store para acceder al estado global
const store = useExtractionStore()

// Estado de los diálogos
const infoDialog = ref(false)
const helpDialog = ref(false)

/**
 * Muestra el diálogo de información
 */
function showInfo() {
  infoDialog.value = true
}

/**
 * Muestra el diálogo de ayuda
 */
function showHelp() {
  helpDialog.value = true
}
</script>

<style scoped>
.q-toolbar {
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.q-page {
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.q-footer .q-toolbar {
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.nav-active {
  background: rgba(255, 255, 255, 0.15);
  font-weight: 600;
}
</style>
