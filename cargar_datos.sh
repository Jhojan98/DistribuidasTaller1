#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
SQL_FILE="${DIR}/cargar_500_datos.sql"

# Si se pasa un argumento, permite especificar otro archivo .sql (ej: ./cargar_datos.sh Hobbies.sql)
if [ -n "$1" ]; then
  SQL_FILE="${DIR}/$1"
fi

echo "=========================================================="
echo "  Cargando Base de Datos 'hobbies' en el Clúster Distribuido"
echo "  Archivo a ejecutar: $(basename "${SQL_FILE}")"
echo "=========================================================="

# 1. Crear base de datos si no existe
echo "--> [1/3] Verificando base de datos 'hobbies'..."
docker exec -i roach1 ./cockroach sql --insecure --host=roach1:26257 -e "CREATE DATABASE IF NOT EXISTS hobbies;"

# 2. Cargar tablas y datos
echo "--> [2/3] Ejecutando $(basename "${SQL_FILE}")..."
docker exec -i roach1 ./cockroach sql --insecure --host=roach1:26257 --database=hobbies < "${SQL_FILE}"

# 3. Validar contenido
echo "--> [3/3] Verificando conteo de registros en las tablas..."
docker exec -i roach1 ./cockroach sql --insecure --host=roach1:26257 --database=hobbies -e "
SELECT 'ESTUDIANTE' AS tabla, COUNT(*) AS registros FROM ESTUDIANTE
UNION ALL
SELECT 'HOBBY', COUNT(*) FROM HOBBY
UNION ALL
SELECT 'RECOMPENSA', COUNT(*) FROM RECOMPENSA
UNION ALL
SELECT 'ESTUDIANTE_HOBBY', COUNT(*) FROM ESTUDIANTE_HOBBY
UNION ALL
SELECT 'REALIZACION_HOBBY', COUNT(*) FROM REALIZACION_HOBBY;
"

echo "=========================================================="
echo "  ¡Listo! Datos montados y replicados en los 3 nodos."
echo "=========================================================="
