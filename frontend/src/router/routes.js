/*
 * Configuración del router de la aplicación
 * Aquí definimos las rutas de nuestra app y qué componente muestra cada una
 */

import { createRouter, createWebHistory } from 'vue-router'

// Importamos los componentes de las páginas
import IndexPage from '../pages/IndexPage.vue'

// Definimos las rutas de la aplicación
const routes = [
  {
    path: '/',
    // El componente principal tiene un layout propio
    component: () => import('../layouts/MainLayout.vue'),
    children: [
      {
        path: '',
        // Página principal de la aplicación
        component: IndexPage,
        meta: {
          title: 'Extractor de Cédulas'
        }
      }
    ]
  },
  {
    // Redirección para rutas que no existen (404)
    path: '/:catchAll(.*)*',
    component: () => import('../pages/Error404.vue')
  }
]

// Creamos y exportamos el router
export function setupRouter() {
  return createRouter({
    // Usamos modo history para URLs limpias sin hash (#)
    history: createWebHistory(),

    // Pasamos las rutas que definimos arriba
    routes,

    // Configuración para comportamiento de scroll
    scrollBehavior(to, from, savedPosition) {
      // Si hay una posición guardada (cuando usamos el botón atrás), vamos ahí
      if (savedPosition) {
        return savedPosition
      }
      // Si no, vamos al inicio de la página
      return { top: 0 }
    }
  })
}
