@echo off
rem Lanzador para CMD o doble clic. La logica vive en cargar_datos.ps1.
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0cargar_datos.ps1" %*
set "RC=%ERRORLEVEL%"

rem Si se ejecuto con doble clic, pausar para poder leer el resultado.
echo %cmdcmdline% | find /i "%~nx0" >nul
if not errorlevel 1 pause

exit /b %RC%
