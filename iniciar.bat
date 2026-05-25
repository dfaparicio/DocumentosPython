@echo off
title Sistema de Extraccion de Documentos
color 0A

echo ============================================
echo   Sistema de Extraccion de Documentos con IA
echo ============================================
echo.

:: Iniciar Backend (en ventana separada)
echo [1/2] Iniciando Backend (FastAPI)...
start "Backend - FastAPI" cmd /k "cd /d c:\Users\USUARIO\sena\DocumentosPython\backend && uvicorn main:app --reload"

:: Esperar 3 segundos para que el backend arranque
timeout /t 3 /nobreak >nul

:: Iniciar Frontend (en ventana separada)
echo [2/2] Iniciando Frontend (Vue.js)...
start "Frontend - Vue.js" cmd /k "cd /d c:\Users\USUARIO\sena\DocumentosPython\frontend && pnpm run dev"

:: Esperar 5 segundos y abrir el navegador
timeout /t 5 /nobreak >nul

echo.
echo ============================================
echo   Todo listo! Abriendo navegador...
echo ============================================
echo.
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:5173
echo   API Docs: http://localhost:8000/docs
echo.
echo   Para detener: cierra las ventanas del servidor
echo ============================================

:: Abrir el navegador automaticamente
start http://localhost:5173

echo.
echo Puedes cerrar esta ventana.
pause
