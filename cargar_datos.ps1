<#
.SYNOPSIS
    Carga la base de datos 'hobbies' en el clúster distribuido de CockroachDB.

.DESCRIPTION
    Equivalente Windows de cargar_datos.sh:
      1. Crea la base de datos 'hobbies' si no existe.
      2. Ejecuta el archivo .sql indicado (por defecto cargar_datos.sql).
      3. Muestra el conteo de registros por tabla.

.PARAMETER SqlFile
    Archivo .sql a ejecutar. Por defecto: cargar_datos.sql.

.EXAMPLE
    .\cargar_datos.ps1

.EXAMPLE
    .\cargar_datos.ps1 Hobbies.sql
#>
[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string]$SqlFile = 'cargar_datos.sql'
)

$ErrorActionPreference = 'Stop'

# Forzar salida UTF-8 para que los acentos se vean bien en cualquier consola.
try { [Console]::OutputEncoding = New-Object System.Text.UTF8Encoding $false } catch { }

# --- Configuración --------------------------------------------------------
$Container = 'roach1'
$Database  = 'hobbies'
$HostAddr  = "${Container}:26257"

# --- Rutas ----------------------------------------------------------------
$BaseDir = $PSScriptRoot
if ([System.IO.Path]::IsPathRooted($SqlFile)) {
    $SqlPath = $SqlFile
}
else {
    $SqlPath = Join-Path $BaseDir $SqlFile
}

function Write-Banner {
    param([string[]]$Lines)

    Write-Host '=========================================================='
    foreach ($Line in $Lines) { Write-Host $Line }
    Write-Host '=========================================================='
}

function Invoke-CockroachSql {
    param(
        [string]$Query,
        [string]$DatabaseName,
        [string]$InputFile
    )

    $DockerArgs = @('exec', '-i', $Container, './cockroach', 'sql', '--insecure', "--host=$HostAddr")
    if ($DatabaseName) { $DockerArgs += "--database=$DatabaseName" }

    if ($InputFile) {
        # Start-Process con -RedirectStandardInput envía el archivo byte a byte,
        # igual que '<' en bash. Un pipe de PowerShell podría alterar la codificación.
        $Process = Start-Process -FilePath $script:DockerExe -ArgumentList $DockerArgs `
            -RedirectStandardInput $InputFile -NoNewWindow -Wait -PassThru
        $ExitCode = $Process.ExitCode
    }
    else {
        $DockerArgs += @('-e', $Query)
        & $script:DockerExe @DockerArgs
        $ExitCode = $LASTEXITCODE
    }

    if ($ExitCode -ne 0) {
        throw "El comando de CockroachDB terminó con código $ExitCode."
    }
}

# --- Comprobaciones previas ----------------------------------------------
$DockerCmd = Get-Command docker -ErrorAction SilentlyContinue
if (-not $DockerCmd) {
    Write-Host 'ERROR: Docker no está instalado o no está en el PATH.' -ForegroundColor Red
    exit 1
}
$script:DockerExe = $DockerCmd.Source

$Running = & $script:DockerExe ps --filter "name=^${Container}$" --format '{{.Names}}' 2>$null
if ($Running -notcontains $Container) {
    Write-Host "ERROR: el contenedor '$Container' no está en ejecución." -ForegroundColor Red
    Write-Host '       Levántalo con: docker compose up -d'
    exit 1
}

if (-not (Test-Path -LiteralPath $SqlPath -PathType Leaf)) {
    Write-Host "ERROR: no se encontró el archivo SQL: $SqlPath" -ForegroundColor Red
    exit 1
}

$SqlName = Split-Path -Leaf $SqlPath

# --- Carga ----------------------------------------------------------------
try {
    Write-Banner @(
        "  Cargando Base de Datos '$Database' en el Clúster Distribuido",
        "  Archivo a ejecutar: $SqlName"
    )

    Write-Host "--> [1/3] Verificando base de datos '$Database'..." -ForegroundColor Cyan
    Invoke-CockroachSql -Query "CREATE DATABASE IF NOT EXISTS $Database;"

    Write-Host "--> [2/3] Ejecutando $SqlName..." -ForegroundColor Cyan
    Invoke-CockroachSql -DatabaseName $Database -InputFile $SqlPath

    Write-Host '--> [3/3] Verificando conteo de registros en las tablas...' -ForegroundColor Cyan
    $CountQuery = @'
SELECT 'ESTUDIANTE' AS tabla, COUNT(*) AS registros FROM ESTUDIANTE
UNION ALL
SELECT 'HOBBY', COUNT(*) FROM HOBBY
UNION ALL
SELECT 'RECOMPENSA', COUNT(*) FROM RECOMPENSA
UNION ALL
SELECT 'ESTUDIANTE_HOBBY', COUNT(*) FROM ESTUDIANTE_HOBBY
UNION ALL
SELECT 'REALIZACION_HOBBY', COUNT(*) FROM REALIZACION_HOBBY;
'@
    Invoke-CockroachSql -DatabaseName $Database -Query $CountQuery

    Write-Banner @('  ¡Listo! Datos montados y replicados en los 3 nodos.')
}
catch {
    Write-Host ''
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
