# Script para limpiar variables de entorno y reiniciar
Write-Host "Limpiando variables de entorno antiguas..." -ForegroundColor Yellow

# Limpiar variables de Odoo del entorno actual
Remove-Item Env:\ODOO_URL -ErrorAction SilentlyContinue
Remove-Item Env:\ODOO_DB -ErrorAction SilentlyContinue
Remove-Item Env:\ODOO_USER -ErrorAction SilentlyContinue
Remove-Item Env:\ODOO_PASSWORD -ErrorAction SilentlyContinue

Write-Host "Variables limpiadas" -ForegroundColor Green
Write-Host ""
Write-Host "Activando entorno virtual..." -ForegroundColor Cyan
& "$PSScriptRoot\venv\Scripts\Activate.ps1"

Write-Host ""
Write-Host "Verificando .env actual:" -ForegroundColor Cyan
python check_env.py

Write-Host ""
Write-Host "Iniciando aplicacion..." -ForegroundColor Green
python app.py
