import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import './css/app.css'

// Router
const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('./pages/Home.vue')
    },
    {
      path: '/comparar',
      name: 'compare',
      component: () => import('./pages/Compare.vue')
    }
  ]
})

// Pinia
const pinia = createPinia()

// App
const app = createApp(App)
app.use(pinia)
app.use(router)
app.mount('#app')
