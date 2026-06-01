<template>
  <div class="compare-page">
    <div class="container">
      <!-- Header -->
      <header class="header">
        <h1 class="title">
          <span class="text-gradient">Reconciliar Documentos</span>
        </h1>
        <p class="subtitle">
          Compara dos archivos Excel verificando que contengan las mismas cédulas, sin importar el orden de las filas.
        </p>
      </header>



      <!-- Sección 2: Comparar -->
      <div class="compare-grid">
        <!-- Archivo A -->
        <div class="card">
          <div class="card-header">
            <h3 class="card-title">📄 Archivo 1</h3>
          </div>
          <div
            class="drop-zone"
            :class="{ dragging: isDraggingA }"
            @dragover.prevent="isDraggingA = true"
            @dragleave.prevent="isDraggingA = false"
            @drop.prevent="onDropA"
            @click="inputA?.click()"
          >
            <span v-if="!store.fileA">Arrastra un Excel aquí</span>
            <span v-else class="file-selected">✅ {{ store.fileA.name }}</span>
            <input ref="inputA" type="file" accept=".xlsx,.xls" class="hidden-input" @change="onSelectA" />
          </div>
          <button v-if="store.hasFileA" class="btn btn-sm btn-outline q-mt-sm" @click="store.clearFileA()">
            Quitar archivo
          </button>
        </div>

        <!-- Archivo B -->
        <div class="card">
          <div class="card-header">
            <h3 class="card-title">📄 Archivo 2</h3>
          </div>
          <div
            class="drop-zone"
            :class="{ dragging: isDraggingB }"
            @dragover.prevent="isDraggingB = true"
            @dragleave.prevent="isDraggingB = false"
            @drop.prevent="onDropB"
            @click="inputB?.click()"
          >
            <span v-if="!store.fileB">Arrastra un Excel aquí</span>
            <span v-else class="file-selected">✅ {{ store.fileB.name }}</span>
            <input ref="inputB" type="file" accept=".xlsx,.xls" class="hidden-input" @change="onSelectB" />
          </div>
          <button v-if="store.hasFileB" class="btn btn-sm btn-outline q-mt-sm" @click="store.clearFileB()">
            Quitar archivo
          </button>
        </div>
      </div>

      <!-- Botón Comparar -->
      <div class="text-center q-mt-lg">
        <button
          class="btn btn-primary btn-lg"
          :disabled="!store.hasBothFiles || loading"
          @click="handleCompare"
        >
          <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"/>
          </svg>
          Comparar Archivos
        </button>
      </div>

      <!-- ===== REPORTE VISUAL DE RESULTADOS ===== -->
      <div v-if="store.hasResult" class="q-mt-lg">

        <!-- Banner principal -->
        <div class="result-banner" :class="store.allClear ? 'result-banner-ok' : 'result-banner-warn'">
          <div class="result-banner-icon">
            <span v-if="store.allClear">✅</span>
            <span v-else>⚠️</span>
          </div>
          <div>
            <h3 class="result-banner-title">
              {{ store.allClear ? 'Sin incongruencias' : 'Se encontraron inconsistencias' }}
            </h3>
            <p class="result-banner-desc">{{ store.success }}</p>
          </div>
        </div>

        <!-- Estadísticas rápidas -->
        <div v-if="store.stats" class="stats-grid q-mt-md">
          <div class="stat-card">
            <span class="stat-number">{{ store.stats.cedulas_archivo_1 }}</span>
            <span class="stat-label">Cédulas Archivo 1</span>
          </div>
          <div class="stat-card">
            <span class="stat-number">{{ store.stats.cedulas_archivo_2 }}</span>
            <span class="stat-label">Cédulas Archivo 2</span>
          </div>
          <div class="stat-card" :class="{ 'stat-ok': store.stats.emparejados > 0 }">
            <span class="stat-number">{{ store.stats.emparejados }}</span>
            <span class="stat-label">Coinciden</span>
          </div>
          <div class="stat-card" :class="{ 'stat-error': (store.stats.solo_en_1 + store.stats.solo_en_2) > 0 }">
            <span class="stat-number">{{ store.stats.solo_en_1 + store.stats.solo_en_2 }}</span>
            <span class="stat-label">No coinciden</span>
          </div>
        </div>

        <!-- Discrepancias por campo -->
        <div v-if="store.stats?.discrepancias_por_campo" class="card q-mt-md">
          <h3 class="card-title q-mb-md">Discrepancias por campo</h3>
          <div class="field-grid">
            <div
              v-for="(count, field) in store.stats.discrepancias_por_campo"
              :key="field"
              class="field-item"
              :class="{ 'field-ok': count === 0, 'field-bad': count > 0 }"
            >
              <span class="field-name">{{ field }}</span>
              <span class="field-count">{{ count }}</span>
            </div>
          </div>
        </div>

        <!-- Detalle de discrepancias -->
        <div v-if="store.discrepancies.length > 0" class="card q-mt-md">
          <h3 class="card-title q-mb-md">Detalle de inconsistencias</h3>
          <div
            v-for="(disc, idx) in store.discrepancies"
            :key="idx"
            class="disc-item"
          >
            <div class="disc-header">
              <span class="disc-badge">Cédula: {{ disc.cedula }}</span>
              <span class="disc-count">{{ disc.campos_diferentes }} campo(s) diferente(s)</span>
            </div>
            <div class="disc-fields">
              <div
                v-for="field in disc.detalle"
                :key="field.campo"
                class="disc-field"
                :class="{ 'disc-field-match': field.coincide, 'disc-field-diff': !field.coincide }"
              >
                <span class="disc-field-name">{{ field.campo }}</span>
                <div class="disc-field-values">
                  <span class="disc-val">{{ field.valor_a || '(vacío)' }}</span>
                  <span class="disc-arrow">→</span>
                  <span class="disc-val">{{ field.valor_b || '(vacío)' }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Registros sin par -->
        <div v-if="store.onlyInA.length > 0" class="card q-mt-md">
          <h3 class="card-title q-mb-md">⚠️ Solo en Archivo 1 ({{ store.onlyInA.length }})</h3>
          <p class="card-desc q-mb-sm">Estas cédulas están en el Archivo 1 pero NO en el Archivo 2</p>
          <div class="no-match-list">
            <div v-for="(r, idx) in store.onlyInA" :key="idx" class="no-match-item">
              <span class="no-match-cedula">{{ r.cedula }}</span>
              <span class="no-match-name">{{ r.nombres }} {{ r.apellidos }}</span>
            </div>
          </div>
        </div>

        <div v-if="store.onlyInB.length > 0" class="card q-mt-md">
          <h3 class="card-title q-mb-md">⚠️ Solo en Archivo 2 ({{ store.onlyInB.length }})</h3>
          <p class="card-desc q-mb-sm">Estas cédulas están en el Archivo 2 pero NO en el Archivo 1</p>
          <div class="no-match-list">
            <div v-for="(r, idx) in store.onlyInB" :key="idx" class="no-match-item">
              <span class="no-match-cedula">{{ r.cedula }}</span>
              <span class="no-match-name">{{ r.nombres }} {{ r.apellidos }}</span>
            </div>
          </div>
        </div>

        <!-- Botón descargar Excel -->
        <div class="text-center q-mt-lg q-mb-lg">
          <button class="btn btn-primary btn-lg" @click="downloadReport">
            <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 10l5 5 5-5"/>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15V3"/>
            </svg>
            Descargar Reporte Excel
          </button>
        </div>
      </div>



      <!-- Mensaje de error -->
      <div v-if="store.error" class="alert alert-error q-mt-md">
        {{ store.error }}
      </div>
    </div>

    <!-- Loading Overlay -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-content">
        <div class="spinner"></div>
        <p class="loading-text">{{ store.loadingMessage || 'Procesando...' }}</p>
        <p class="loading-subtext">Esto puede tardar unos segundos</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useComparisonStore } from '../stores/comparison'
import { useComparison } from '../composables/useComparison'

const store = useComparisonStore()
const { reconcileFiles, downloadReport } = useComparison()

// Refs para inputs
const inputA = ref(null)
const inputB = ref(null)

// Estado de drag local
const isDraggingA = ref(false)
const isDraggingB = ref(false)

// Computed
const loading = computed(() => store.loading)



// === Archivo A ===
function onDropA(e) {
  isDraggingA.value = false
  const file = e.dataTransfer.files[0]
  if (file) store.setFileA(file)
}

function onSelectA(e) {
  const file = e.target.files[0]
  if (file) store.setFileA(file)
  e.target.value = ''
}

// === Archivo B ===
function onDropB(e) {
  isDraggingB.value = false
  const file = e.dataTransfer.files[0]
  if (file) store.setFileB(file)
}

function onSelectB(e) {
  const file = e.target.files[0]
  if (file) store.setFileB(file)
  e.target.value = ''
}

// === Comparar ===
async function handleCompare() {
  if (!store.hasBothFiles) return
  await reconcileFiles(store.fileA, store.fileB)
}
</script>

<style scoped>
.compare-page {
  min-height: 100vh;
  padding-bottom: 40px;
}

.container {
  max-width: 900px;
  margin: 0 auto;
  padding: 0 16px;
}

/* Header */
.header {
  text-align: center;
  margin-bottom: 32px;
  padding-top: 16px;
}

.title {
  font-size: 32px;
  font-weight: 700;
  color: var(--gray-800, #1f2937);
  margin-bottom: 12px;
}

.text-gradient {
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  font-size: 16px;
  color: var(--gray-600, #4b5563);
  max-width: 600px;
  margin: 0 auto;
  line-height: 1.6;
}

/* Cards */
.card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06);
  border: 1px solid var(--gray-200, #e5e7eb);
}

.card-header {
  margin-bottom: 16px;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--gray-800, #1f2937);
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 4px 0;
}

.card-desc {
  font-size: 14px;
  color: var(--gray-500, #6b7280);
  margin: 0;
}

.card-icon {
  width: 22px;
  height: 22px;
  color: #4f46e5;
}

/* Row layout */
.row-items {
  display: flex;
  gap: 12px;
  align-items: center;
}

.flex-grow {
  flex: 1;
}

/* Drop Zone */
.drop-zone {
  border: 2px dashed var(--gray-300, #d1d5db);
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  color: var(--gray-500, #6b7280);
  font-size: 14px;
  min-height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.drop-zone:hover {
  border-color: #4f46e5;
  background: rgba(79, 70, 229, 0.03);
}

.drop-zone.dragging {
  border-color: #4f46e5;
  background: rgba(79, 70, 229, 0.08);
  transform: scale(1.01);
}

.file-selected {
  color: #059669;
  font-weight: 500;
}

.upload-icon-sm {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.hidden-input {
  display: none;
}

/* Compare Grid */
.compare-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

/* Divider */
.divider {
  display: flex;
  align-items: center;
  margin: 32px 0;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--gray-200, #e5e7eb);
}

.divider-text {
  padding: 0 16px;
  font-size: 14px;
  font-weight: 600;
  color: var(--gray-400, #9ca3af);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* Buttons */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: #4f46e5;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #4338ca;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
}

.btn-outline {
  background: transparent;
  color: #4f46e5;
  border: 1px solid #4f46e5;
  padding: 6px 12px;
  font-size: 12px;
}

.btn-outline:hover {
  background: rgba(79, 70, 229, 0.05);
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
}

.btn-lg {
  padding: 14px 28px;
  font-size: 16px;
}

.btn-icon {
  width: 18px;
  height: 18px;
}

/* === Result Banner === */
.result-banner {
  border-radius: 12px;
  padding: 20px 24px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.result-banner-ok {
  background: linear-gradient(135deg, #ecfdf5, #d1fae5);
  border: 2px solid #059669;
}

.result-banner-warn {
  background: linear-gradient(135deg, #fefce8, #fef3c7);
  border: 2px solid #d97706;
}

.result-banner-icon {
  font-size: 36px;
  flex-shrink: 0;
}

.result-banner-title {
  font-size: 20px;
  font-weight: 700;
  margin: 0;
}

.result-banner-ok .result-banner-title {
  color: #065f46;
}

.result-banner-warn .result-banner-title {
  color: #92400e;
}

.result-banner-desc {
  font-size: 14px;
  margin: 4px 0 0 0;
  opacity: 0.8;
}

/* === Stats Grid === */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.stat-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 16px;
  text-align: center;
}

.stat-number {
  display: block;
  font-size: 28px;
  font-weight: 700;
  color: #4f46e5;
}

.stat-label {
  display: block;
  font-size: 12px;
  color: #6b7280;
  margin-top: 4px;
}

.stat-error .stat-number {
  color: #dc2626;
}

.stat-ok .stat-number {
  color: #059669;
}

.stat-warn .stat-number {
  color: #d97706;
}

/* === Field Grid === */
.field-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.field-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 14px;
}

.field-ok {
  background: #ecfdf5;
  border: 1px solid #a7f3d0;
}

.field-bad {
  background: #fef2f2;
  border: 1px solid #fecaca;
}

.field-name {
  color: #374151;
  font-weight: 500;
}

.field-count {
  font-weight: 700;
  min-width: 24px;
  text-align: center;
}

.field-ok .field-count {
  color: #059669;
}

.field-bad .field-count {
  color: #dc2626;
}

/* === Discrepancy Detail === */
.disc-item {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  margin-bottom: 12px;
  overflow: hidden;
}

.disc-header {
  background: #fef2f2;
  padding: 12px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #fecaca;
}

.disc-badge {
  font-weight: 600;
  color: #991b1b;
  font-size: 14px;
}

.disc-count {
  font-size: 13px;
  color: #dc2626;
}

.disc-fields {
  padding: 8px 0;
}

.disc-field {
  display: flex;
  align-items: center;
  padding: 8px 16px;
  gap: 12px;
  font-size: 13px;
}

.disc-field-match {
  background: #ecfdf5;
}

.disc-field-diff {
  background: #fef2f2;
}

.disc-field-name {
  min-width: 140px;
  font-weight: 600;
  color: #374151;
}

.disc-field-values {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.disc-val {
  background: white;
  padding: 4px 10px;
  border-radius: 4px;
  border: 1px solid #e5e7eb;
  font-size: 13px;
}

.disc-arrow {
  color: #9ca3af;
  font-weight: bold;
}

/* === No Match List === */
.no-match-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.no-match-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  background: #fef9c3;
  border-radius: 6px;
  border: 1px solid #fde68a;
  font-size: 14px;
}

.no-match-cedula {
  font-weight: 600;
  color: #92400e;
  min-width: 120px;
}

.no-match-name {
  color: #78716c;
}

/* Alerts */
.alert {
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 14px;
}

.alert-error {
  background: #fef2f2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

.alert-success {
  background: #ecfdf5;
  color: #065f46;
  border: 1px solid #a7f3d0;
}

/* Loading */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255,255,255,0.95);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.loading-content {
  text-align: center;
}

.spinner {
  width: 48px;
  height: 48px;
  border: 4px solid #e5e7eb;
  border-top: 4px solid #4f46e5;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  font-size: 20px;
  font-weight: 600;
  color: var(--gray-800, #1f2937);
  margin-bottom: 4px;
}

.loading-subtext {
  font-size: 14px;
  color: var(--gray-500, #6b7280);
}

/* Responsive */
@media (max-width: 768px) {
  .compare-grid {
    grid-template-columns: 1fr;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .field-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .row-items {
    flex-direction: column;
  }

  .title {
    font-size: 24px;
  }

  .subtitle {
    font-size: 14px;
  }

  .disc-field {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }

  .disc-field-name {
    min-width: unset;
  }
}
</style>
