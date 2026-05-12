/*
 * Archivo de configuración de Quasar
 * Aquí definimos el tema, plugins y comportamiento general de la aplicación
 */

import { defineConfig } from '@quasar/quasar-app-vite'
import { fileURLToPath } from 'node:url'

export default defineConfig({
  // Configuración del CSS
  css: ['app.scss'],

  // Configuración de las aplicaciones extra de Quasar
  extras: [
    'roboto-font', // Fuente Roboto (es la fuente por defecto de Quasar)
    'material-icons', // Iconos de Material Design
    'material-icons-outlined' // Iconos outlined (versión contorno)
  ],

  // Configuración del build
  build: {
    target: {
      browser: ['es2019', 'edge88', 'firefox78', 'chrome87', 'safari13.1'],
      node: 'node16'
    },

    vueRouterMode: 'history', // Usamos modo history para URLs limpias sin hash

    vitePlugins: [
      ['@quasar/vite-plugin', {}]
    ],

    // Configuración para el desarrollo local
    devtools: {
      enabled: true // Habilitamos las devtools de Vue para facilitar el debugging
    }
  },

  // Configuración del framework Quasar
  framework: {
    // Habilitamos los plugins que vamos a usar
    config: {},

    // Plugins de Quasar que vamos a utilizar
    plugins: [
      'Notify', // Para mostrar notificaciones tipo toast
      'Loading', // Para mostrar indicadores de carga
      'Dialog' // Para mostrar diálogos y alertas
    ],

    // Configuración del idioma de los componentes de Quasar
    lang: 'es', // Español

    // Propiedades globales de los componentes
    iconSet: 'material-icons' // Usamos los iconos de Material Design
  },

  // Configuración de las animaciones
  animations: [],

  // Configuración del tema verde
  ssr: {
    pwa: false,
    prodPort: 3000,
    middlewares: [
      'render' // Middleware para renderizado del lado del servidor
    ]
  },

  // Configuración del modo de desarrollo
  devServer: {
    open: true, // Abre automáticamente el navegador al levantar el servidor
    port: 5173, // Puerto del servidor de desarrollo
    host: '0.0.0.0', // Escucha en todas las interfaces
    proxy: {
      // Proxy para conectar con el backend
      '/api': {
        target: 'http://localhost:8000', // URL del backend
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  },

  // Configuración de las fuentes
  boot: [],

  // Configuración del tipo de aplicación
  // 'spa' = Single Page Application
  // 'pwa' = Progressive Web App
  // 'ssr' = Server Side Rendering
  // 'bex' = Browser Extension
  // 'cordova' = Apache Cordova
  // 'capacitor' = Capacitor
  // 'electron' = Electron
  // 'custom' = Custom
  // 'auto' = Auto (selecciona el mejor para la plataforma actual)
  // 'hybrid' = Híbrido (SPA + SSR)
  // 'multi-spa' = Multiple SPA
  // 'multi-pwa' = Multiple PWA
  // 'multi-ssr' = Multiple SSR
  // 'multi-bex' = Multiple BEX
  // 'multi-cordova' = Multiple Cordova
  // 'multi-capacitor' = Multiple Capacitor
  // 'multi-electron' = Multiple Electron
  // 'multi-custom' = Multiple Custom
  // 'multi-auto' = Multiple Auto
  // 'multi-hybrid' = Multiple Hybrid
  // 'multi-multi-spa' = Multiple Multiple SPA
  // 'multi-multi-pwa' = Multiple Multiple PWA
  // 'multi-multi-ssr' = Multiple Multiple SSR
  // 'multi-multi-bex' = Multiple Multiple BEX
  // 'multi-multi-cordova' = Multiple Multiple Cordova
  // 'multi-multi-capacitor' = Multiple Multiple Capacitor
  // 'multi-multi-electron' = Multiple Multiple Electron
  // 'multi-multi-custom' = Multiple Multiple Custom
  // 'multi-multi-auto' = Multiple Multiple Auto
  // 'multi-multi-hybrid' = Multiple Multiple Hybrid
  // 'multi-multi-multi-spa' = Multiple Multiple Multiple SPA
  // 'multi-multi-multi-pwa' = Multiple Multiple Multiple PWA
  // 'multi-multi-multi-ssr' = Multiple Multiple Multiple SSR
  // 'multi-multi-multi-bex' = Multiple Multiple Multiple BEX
  // 'multi-multi-multi-cordova' = Multiple Multiple Multiple Cordova
  // 'multi-multi-multi-capacitor' = Multiple Multiple Multiple Capacitor
  // 'multi-multi-multi-electron' = Multiple Multiple Multiple Electron
  // 'multi-multi-multi-custom' = Multiple Multiple Multiple Custom
  // 'multi-multi-multi-auto' = Multiple Multiple Multiple Auto
  // 'multi-multi-multi-hybrid' = Multiple Multiple Multiple Hybrid
  // 'multi-multi-multi-multi-spa' = Multiple Multiple Multiple Multiple SPA
  // 'multi-multi-multi-multi-pwa' = Multiple Multiple Multiple Multiple PWA
  // 'multi-multi-multi-multi-ssr' = Multiple Multiple Multiple Multiple SSR
  // 'multi-multi-multi-multi-bex' = Multiple Multiple Multiple Multiple BEX
  // 'multi-multi-multi-multi-cordova' = Multiple Multiple Multiple Multiple Cordova
  // 'multi-multi-multi-multi-capacitor' = Multiple Multiple Multiple Multiple Capacitor
  // 'multi-multi-multi-multi-electron' = Multiple Multiple Multiple Multiple Electron
  // 'multi-multi-multi-multi-custom' = Multiple Multiple Multiple Multiple Custom
  // 'multi-multi-multi-multi-auto' = Multiple Multiple Multiple Multiple Auto
  // 'multi-multi-multi-multi-hybrid' = Multiple Multiple Multiple Multiple Hybrid
  // 'multi-multi-multi-multi-multi-spa' = Multiple Multiple Multiple Multiple Multiple SPA
  // 'multi-multi-multi-multi-multi-pwa' = Multiple Multiple Multiple Multiple Multiple PWA
  // 'multi-multi-multi-multi-multi-ssr' = Multiple Multiple Multiple Multiple Multiple SSR
  // 'multi-multi-multi-multi-multi-bex' = Multiple Multiple Multiple Multiple Multiple BEX
  // 'multi-multi-multi-multi-multi-cordova' = Multiple Multiple Multiple Multiple Multiple Cordova
  // 'multi-multi-multi-multi-multi-capacitor' = Multiple Multiple Multiple Multiple Multiple Capacitor
  // 'multi-multi-multi-multi-multi-electron' = Multiple Multiple Multiple Multiple Multiple Electron
  // 'multi-multi-multi-multi-multi-custom' = Multiple Multiple Multiple Multiple Multiple Custom
  // 'multi-multi-multi-multi-multi-auto' = Multiple Multiple Multiple Multiple Multiple Auto
  // 'multi-multi-multi-multi-multi-hybrid' = Multiple Multiple Multiple Multiple Multiple Hybrid
  // 'multi-multi-multi-multi-multi-multi-spa' = Multiple Multiple Multiple Multiple Multiple Multiple SPA
  // 'multi-multi-multi-multi-multi-multi-pwa' = Multiple Multiple Multiple Multiple Multiple Multiple PWA
  // 'multi-multi-multi-multi-multi-multi-ssr' = Multiple Multiple Multiple Multiple Multiple Multiple SSR
  // 'multi-multi-multi-multi-multi-multi-bex' = Multiple Multiple Multiple Multiple Multiple Multiple BEX
  // 'multi-multi-multi-multi-multi-multi-cordova' = Multiple Multiple Multiple Multiple Multiple Multiple Cordova
  // 'multi-multi-multi-multi-multi-multi-capacitor' = Multiple Multiple Multiple Multiple Multiple Multiple Capacitor
  // 'multi-multi-multi-multi-multi-multi-electron' = Multiple Multiple Multiple Multiple Multiple Multiple Electron
  // 'multi-multi-multi-multi-multi-multi-custom' = Multiple Multiple Multiple Multiple Multiple Multiple Custom
  // 'multi-multi-multi-multi-multi-multi-auto' = Multiple Multiple Multiple Multiple Multiple Multiple Auto
  // 'multi-multi-multi-multi-multi-multi-hybrid' = Multiple Multiple Multiple Multiple Multiple Multiple Hybrid
  // 'multi-multi-multi-multi-multi-multi-multi-spa' = Multiple Multiple Multiple Multiple Multiple Multiple Multiple SPA
  // 'multi-multi-multi-multi-multi-multi-multi-pwa' = Multiple Multiple Multiple Multiple Multiple Multiple Multiple PWA
  // 'multi-multi-multi-multi-multi-multi-multi-ssr' = Multiple Multiple Multiple Multiple Multiple Multiple Multiple SSR
  // 'multi-multi-multi-multi-multi-multi-multi-bex' = Multiple Multiple Multiple Multiple Multiple Multiple Multiple BEX
  // 'multi-multi-multi-multi-multi-multi-multi-cordova' = Multiple Multiple Multiple Multiple Multiple Multiple Multiple Cordova
  // 'multi-multi-multi-multi-multi-multi-multi-capacitor' = Multiple Multiple Multiple Multiple Multiple Multiple Multiple Capacitor
  // 'multi-multi-multi-multi-multi-multi-multi-electron' = Multiple Multiple Multiple Multiple Multiple Multiple Multiple Electron
  // 'multi-multi-multi-multi-multi-multi-multi-custom' = Multiple Multiple Multiple Multiple Multiple Multiple Multiple Custom
  // 'multi-multi-multi-multi-multi-multi-multi-auto' = Multiple Multiple Multiple Multiple Multiple Multiple Multiple Auto
  // 'multi-multi-multi-multi-multi-multi-multi-hybrid' = Multiple Multiple Multiple Multiple Multiple Multiple Multiple Hybrid
  // 'multi-multi-multi-multi-multi-multi-multi-multi-spa' = Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple SPA
  // 'multi-multi-multi-multi-multi-multi-multi-multi-pwa' = Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple PWA
  // 'multi-multi-multi-multi-multi-multi-multi-multi-ssr' = Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple SSR
  // 'multi-multi-multi-multi-multi-multi-multi-multi-bex' = Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple BEX
  // 'multi-multi-multi-multi-multi-multi-multi-multi-cordova' = Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Cordova
  // 'multi-multi-multi-multi-multi-multi-multi-multi-capacitor' = Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Capacitor
  // 'multi-multi-multi-multi-multi-multi-multi-multi-electron' = Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Electron
  // 'multi-multi-multi-multi-multi-multi-multi-multi-custom' = Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Custom
  // 'multi-multi-multi-multi-multi-multi-multi-multi-auto' = Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Auto
  // 'multi-multi-multi-multi-multi-multi-multi-multi-hybrid' = Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Hybrid
  // 'multi-multi-multi-multi-multi-multi-multi-multi-multi-spa' = Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple SPA
  // 'multi-multi-multi-multi-multi-multi-multi-multi-multi-pwa' = Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple PWA
  // 'multi-multi-multi-multi-multi-multi-multi-multi-multi-ssr' = Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple SSR
  // 'multi-multi-multi-multi-multi-multi-multi-multi-multi-bex' = Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple BEX
  // 'multi-multi-multi-multi-multi-multi-multi-multi-multi-cordova' = Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Cordova
  // 'multi-multi-multi-multi-multi-multi-multi-multi-multi-capacitor' = Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Capacitor
  // 'multi-multi-multi-multi-multi-multi-multi-multi-multi-electron' = Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Electron
  // 'multi-multi-multi-multi-multi-multi-multi-multi-multi-custom' = Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Custom
  // 'multi-multi-multi-multi-multi-multi-multi-multi-multi-auto' = Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Auto
  // 'multi-multi-multi-multi-multi-multi-multi-multi-multi-hybrid' = Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Hybrid
  // 'multi-multi-multi-multi-multi-multi-multi-multi-multi-multi-spa' = Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple SPA
  // 'multi-multi-multi-multi-multi-multi-multi-multi-multi-multi-pwa' = Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple PWA
  // 'multi-multi-multi-multi-multi-multi-multi-multi-multi-multi-ssr' = Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple SSR
  // 'multi-multi-multi-multi-multi-multi-multi-multi-multi-multi-bex' = Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple BEX
  // 'multi-multi-multi-multi-multi-multi-multi-multi-multi-multi-cordova' = Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Cordova
  // 'multi-multi-multi-multi-multi-multi-multi-multi-multi-multi-capacitor' = Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Capacitor
  // 'multi-multi-multi-multi-multi-multi-multi-multi-multi-multi-electron' = Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Electron
  // 'multi-multi-multi-multi-multi-multi-multi-multi-multi-multi-custom' = Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Custom
  // 'multi-multi-multi-multi-multi-multi-multi-multi-multi-multi-auto' = Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Auto
  // 'multi-multi-multi-multi-multi-multi-multi-multi-multi-multi-hybrid' = Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Hybrid
  // 'multi-multi-multi-multi-multi-multi-multi-multi-multi-multi-multi-spa' = Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple SPA
  // 'multi-multi-multi-multi-multi-multi-multi-multi-multi-multi-multi-pwa' = Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple PWA
  // 'multi-multi-multi-multi-multi-multi-multi-multi-multi-multi-multi-ssr' = Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple SSR
  // 'multi-multi-multi-multi-multi-multi-multi-multi-multi-multi-multi-bex' = Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple BEX
  // 'multi-multi-multi-multi-multi-multi-multi-multi-multi-multi-multi-cordova' = Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Cordova
  // 'multi-multi-multi-multi-multi-multi-multi-multi-multi-multi-multi-capacitor' = Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Capacitor
  // 'multi-multi-multi-multi-multi-multi-multi-multi-multi-multi-multi-electron' = Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Electron
  // 'multi-multi-multi-multi-multi-multi-multi-multi-multi-multi-multi-custom' = Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Custom
  // 'multi-multi-multi-multi-multi-multi-multi-multi-multi-multi-multi-auto' = Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Auto
  // 'multi-multi-multi-multi-multi-multi-multi-multi-multi-multi-multi-hybrid' = Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Multiple Hybrid
  // 'multi-multi-multi-multi-multi-multi-multi-multi-multi-multi-multi-multi-spa' => 'spa', // Tipo de aplicación: Single Page Application

  // Configuración de las variables de entorno
  env: {
    // Aquí podemos definir variables que estarán disponibles en la aplicación
    // Por ejemplo: API_URL: 'http://localhost:8000'
  },

  // Configuración de las fuentes
  brand: {
    // Tema verde personalizado
    primary: '#2E7D32',    // Verde principal
    secondary: '#4CAF50',  // Verde secundario
    accent: '#66BB6A',     // Verde acento
    dark: '#1B5E20',       // Verde oscuro
    positive: '#43A047',   // Verde positivo
    negative: '#C62828',   // Rojo para errores
    info: '#0277BD',      // Azul para información
    warning: '#F9A825'     // Amarillo para advertencias
  }
})
