<!--
  Componente para mostrar los datos extraídos en una tabla
  Muestra los nombres, apellidos, número de documento y fecha de nacimiento
-->
<template>
  <div class="data-table">
    <!-- Tarjeta que contiene la tabla -->
    <q-card class="card-shadow">
      <!-- Encabezado de la tabla con título -->
      <q-card-section class="bg-primary text-white q-pa-md">
        <div class="text-h6">
          <q-icon name="table_chart" class="q-mr-sm" />
          Datos Extraídos ({{ data.length }} cédulas)
        </div>
      </q-card-section>

      <!-- Contenido de la tabla -->
      <q-card-section class="q-pa-none">
        <!-- Si hay datos, mostramos la tabla -->
        <q-table
          v-if="data.length > 0"
          :rows="rows"
          :columns="columns"
          row-key="id"
          flat
          bordered
          separator="horizontal"
          :pagination="pagination"
          :rows-per-page-options="[10, 20, 50, 100]"
        >
          <!-- Columna de Nombres -->
          <template v-slot:body-cell-nombres="props">
            <q-td :props="props">
              <div v-if="props.row.nombres" class="text-body2">
                {{ props.row.nombres }}
              </div>
              <div v-else class="text-grey-5 text-italic">
                No disponible
              </div>
            </q-td>
          </template>

          <!-- Columna de Apellidos -->
          <template v-slot:body-cell-apellidos="props">
            <q-td :props="props">
              <div v-if="props.row.apellidos" class="text-body2">
                {{ props.row.apellidos }}
              </div>
              <div v-else class="text-grey-5 text-italic">
                No disponible
              </div>
            </q-td>
          </template>

          <!-- Columna de Número de Documento -->
          <template v-slot:body-cell-numero_documento="props">
            <q-td :props="props">
              <div v-if="props.row.numero_documento" class="text-body2 text-primary text-weight-medium">
                {{ props.row.numero_documento }}
              </div>
              <div v-else class="text-grey-5 text-italic">
                No disponible
              </div>
            </q-td>
          </template>

          <!-- Columna de Fecha de Nacimiento -->
          <template v-slot:body-cell-fecha_nacimiento="props">
            <q-td :props="props">
              <div v-if="props.row.fecha_nacimiento" class="text-body2">
                {{ props.row.fecha_nacimiento }}
              </div>
              <div v-else class="text-grey-5 text-italic">
                No disponible
              </div>
            </q-td>
          </template>

          <!-- Columna de Estado -->
          <template v-slot:body-cell-estado="props">
            <q-td :props="props">
              <q-badge
                :color="hasCompleteData(props.row) ? 'positive' : 'warning'"
                :label="hasCompleteData(props.row) ? 'Completo' : 'Incompleto'"
              />
            </q-td>
          </template>
        </q-table>

        <!-- Si no hay datos, mostramos un mensaje -->
        <div v-else class="q-pa-xl text-center">
          <q-icon
            name="folder_open"
            size="80px"
            color="grey-4"
            class="q-mb-md"
          />
          <div class="text-h6 text-grey-6 q-mb-sm">
            No hay datos para mostrar
          </div>
          <div class="text-body2 text-grey-5">
            Sube un PDF para extraer la información de las cédulas
          </div>
        </div>
      </q-card-section>

      <!-- Pie de la tabla con estadísticas -->
      <q-card-section v-if="data.length > 0" class="q-pa-md bg-grey-1">
        <div class="row items-center justify-between">
          <!-- Contador de registros completos -->
          <div class="text-subtitle2 text-grey-7">
            <q-icon name="check_circle" color="positive" class="q-mr-xs" />
            {{ completeCount }} registros completos
            <span class="q-mx-md">|</span>
            <q-icon name="warning" color="warning" class="q-mr-xs" />
            {{ incompleteCount }} registros incompletos
          </div>

          <!-- Botón para limpiar todos los datos -->
          <q-btn
            flat
            color="negative"
            icon="delete_sweep"
            label="Limpiar todo"
            no-caps
            @click="emit('clear-all')"
          />
        </div>
      </q-card-section>
    </q-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

// Props que recibe el componente
const props = defineProps({
  // Lista de datos extraídos
  data: {
    type: Array,
    default: () => []
  }
})

// Emits para comunicarse con el componente padre
const emit = defineEmits(['clear-all'])

// Configuración de la paginación
const pagination = ref({
  sortBy: 'id',
  descending: false,
  page: 1,
  rowsPerPage: 10
})

// Definición de las columnas de la tabla
const columns = [
  {
    name: 'nombres',
    required: true,
    label: 'Nombres',
    align: 'left',
    field: 'nombres',
    sortable: true
  },
  {
    name: 'apellidos',
    required: true,
    label: 'Apellidos',
    align: 'left',
    field: 'apellidos',
    sortable: true
  },
  {
    name: 'numero_documento',
    required: true,
    label: 'Número de Documento',
    align: 'left',
    field: 'numero_documento',
    sortable: true
  },
  {
    name: 'fecha_nacimiento',
    required: true,
    label: 'Fecha de Nacimiento',
    align: 'left',
    field: 'fecha_nacimiento',
    sortable: true
  },
  {
    name: 'estado',
    required: true,
    label: 'Estado',
    align: 'center',
    field: 'estado',
    sortable: false
  }
]

// Filas de la tabla (agregamos un ID único a cada fila)
const rows = computed(() => {
  return props.data.map((item, index) => ({
    id: index,
    nombres: item.nombres || '',
    apellidos: item.apellidos || '',
    numero_documento: item.numero_documento || '',
    fecha_nacimiento: item.fecha_nacimiento || ''
  }))
})

// Cantidad de registros con datos completos
const completeCount = computed(() => {
  return props.data.filter(item => hasCompleteData(item)).length
})

// Cantidad de registros incompletos
const incompleteCount = computed(() => {
  return props.data.filter(item => !hasCompleteData(item)).length
})

/**
 * Verifica si un registro tiene todos los datos completos
 */
function hasCompleteData(row) {
  return row.nombres && row.apellidos && row.numero_documento && row.fecha_nacimiento
}
</script>

<style scoped>
.data-table {
  width: 100%;
}

.q-table {
  border-radius: 0 0 12px 12px;
}

.q-table thead tr {
  background: linear-gradient(135deg, #2E7D32 0%, #4CAF50 100%);
  color: white;
}

.q-table thead th {
  font-weight: 600;
  font-size: 14px;
}

.q-table tbody tr:hover {
  background-color: rgba(76, 175, 80, 0.05);
}

.q-table tbody tr:nth-child(even) {
  background-color: #fafafa;
}

@media (max-width: 768px) {
  .q-table {
    font-size: 12px;
  }
}
</style>
