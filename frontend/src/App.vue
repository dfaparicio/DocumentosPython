<template>
  <div id="app">
    <!-- Navegación -->
    <nav class="nav-bar">
      <div class="nav-container">
        <div class="nav-brand">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" class="nav-logo">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
          </svg>
          <span class="nav-title">Extractor de Cédulas</span>
        </div>
        <div class="nav-links">
          <router-link to="/" class="nav-link" active-class="nav-link-active" :exact="true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" class="nav-icon">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
            </svg>
            Extraer
          </router-link>
          <router-link to="/comparar" class="nav-link" active-class="nav-link-active">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" class="nav-icon">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"/>
            </svg>
            Comparar
          </router-link>
        </div>
      </div>
    </nav>

    <router-view />
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: #f5f5f5;
}

#app {
  min-height: 100vh;
}

/* Navigation */
.nav-bar {
  background: white;
  border-bottom: 1px solid #e5e7eb;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 56px;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 8px;
}

.nav-logo {
  width: 24px;
  height: 24px;
  color: #4f46e5;
}

.nav-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.nav-links {
  display: flex;
  gap: 4px;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #6b7280;
  text-decoration: none;
  transition: all 0.2s ease;
}

.nav-link:hover {
  color: #4f46e5;
  background: rgba(79, 70, 229, 0.05);
}

.nav-link-active {
  color: #4f46e5;
  background: rgba(79, 70, 229, 0.1);
}

.nav-icon {
  width: 16px;
  height: 16px;
}

@media (max-width: 640px) {
  .nav-title {
    display: none;
  }

  .nav-link {
    padding: 8px 12px;
    font-size: 13px;
  }
}
</style>
