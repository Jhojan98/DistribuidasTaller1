# Orden de ejecucion de experimentos
1. Primero abrir 1 instancia/ventana SQL a partir de cada nodo (3 en total)
2. Segundo copiar y pegar las sentencias SQL de cada archivo en su respectiva instancia

## Experimento 1: Prueba de inserción por fila
1. Nodo1.sql (paso 1)
    - Insertar estudiante 1000
    - Buscarlo para probar
2. Nodo2.sql (paso 2)
    - Probar busqueda estudiante insertado de nodo 1
    - Insertar nuevo estudiante 2000
3. Nodo3.sql (paso 3)
    - Probar busqueda estudiante insertado de nodo 2
    - Eliminar nuevos estudiantes para limpiar

## Experimento 2: Prueba de inserción por columna
1. Nodo1.sql (paso 1)
    - Mostrar columnas estudiante
    - Insertar columna PAIS
    - Mostrar columnas otra vez para comprobar
2. Nodo2.sql (paso 2)
    - Mostrar columnas para comprobar insertada en nodo 1
    - Mostrar estudiante 1 para probar la nueva columna (opcional)
    - Insertar datos en la columna de PAIS
3. Nodo3.sql (paso 3)
    - Mostrar consulta para probar la cantidad de paises insertados en nodo 2
4. Nodo1.sql (paso 4)
    - Probar que en nodo 1 tambien sirve con otra consulta para pais
    - Eliminar nueva columna para limpiar (opcional)
