# Frontend - Extractor de Cédulas

Frontend para la aplicación de extracción de datos de cédulas usando Inteligencia Artificial.

## 🚀 Tecnologías

- **Vue 3** - Framework JavaScript
- **Quasar** - Framework UI
- **Pinia** - Gestión de estado
- **Vue Router** - Enrutamiento
- **Axios** - Cliente HTTP
- **Vite** - Build tool
- **Sass** - Preprocesador CSS

## 📋 Prerrequisitos

- Node.js (v20 o superior)
- npm o yarn

## 🔧 Instalación

1. Instalar dependencias:
```bash
npm install
```

2. Configurar variables de entorno (opcional):
```bash
cp .env.example .env
# Editar .env con la URL del backend
```

## 🎯 Scripts disponibles

### Desarrollo
```bash
npm run dev
```
Inicia el servidor de desarrollo en `http://localhost:5173`

### Build para producción
```bash
npm run build
```
Crea la carpeta `dist/` con los archivos optimizados

### Previsualizar build
```bash
npm run preview
```
Previsualiza la versión de producción

## 📁 Estructura del proyecto

```
frontend/
├── public/              # Archivos estáticos
├── src/
│   ├── assets/         # Imágenes y recursos
│   ├── components/     # Componentes reutilizables
│   ├── composables/    # Lógica reutilizable
│   ├── css/           # Estilos globales
│   ├── layouts/        # Layouts de la aplicación
│   ├── pages/          # Páginas de la aplicación
│   ├── router/         # Configuración de rutas
│   ├── stores/         # Pinia stores
│   ├── App.vue         # Componente raíz
│   └── main.js        # Punto de entrada
├── .env.example        # Plantilla de variables de entorno
├── package.json        # Dependencias del proyecto
├── quasar.config.js    # Configuración de Quasar
└── vite.config.js      # Configuración de Vite
```

## 🎨 Tema

El tema usa colores verdes personalizados:
- **Primario:** #2E7D32
- **Secundario:** #4CAF50
- **Acento:** #66BB6A

## 🔗 Integración con Backend

El frontend se conecta al backend en `http://localhost:8000` por defecto.
Puedes cambiar la URL en el archivo `.env`:

```
VITE_API_URL=http://tu-backend-url.com
```

## 🐛 Problemas comunes

### El backend no responde
Verifica que:
1. El backend esté corriendo en el puerto 8000
2. La URL del backend en `.env` sea correcta
3. No haya problemas de CORS

### Errores de dependencias
```bash
# Eliminar node_modules y reinstalar
rm -rf node_modules package-lock.json
npm install
```

## 📄 Licencia

Este proyecto está bajo la licencia MIT.
