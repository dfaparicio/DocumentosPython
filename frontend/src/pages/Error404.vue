<!--
  Página de error 404
  Se muestra cuando el usuario intenta acceder a una ruta que no existe
-->
<template>
  <q-layout view="hHh lpR fFf">
    <q-page-container>
      <q-page class="flex flex-center bg-grey-1">
        <div class="text-center q-pa-xl">
          <!-- Icono de error grande -->
          <q-icon
            name="error_outline"
            size="150px"
            color="negative"
            class="q-mb-md"
          />

          <!-- Mensaje principal -->
          <h1 class="text-h3 text-grey-9 q-mb-md">
            Página no encontrada
          </h1>

          <!-- Mensaje secundario -->
          <p class="text-h6 text-grey-7 q-mb-xl">
            Lo sentimos, la página que buscas no existe.
          </p>

          <!-- Botón para volver al inicio -->
          <q-btn
            to="/"
            color="primary"
            size="lg"
            rounded
            icon="home"
            label="Volver al inicio"
            no-caps
          />
        </div>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script>
export default {
  name: 'Error404'
}
</script>

<style scoped>
/* Animación suave para el icono */
.q-icon {
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}
</style>
