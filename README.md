# 🚀 Guía de Base de Datos Distribuida: CockroachDB & Hobbies

Este documento explica de forma clara, didáctica y práctica qué es una base de datos distribuida, cómo funciona el clúster de **CockroachDB** configurado en esta carpeta, por qué tu configuración anterior no terminaba de arrancar y cómo montar tu base de datos SQL de `Hobbies/` sin fricciones.

---

## 📌 Tabla de Contenidos
1. [¿Servía el Docker que tenías? ¿Qué le faltaba?](#1-servía-el-docker-que-tenías-qué-le-faltaba)
2. [¿Qué es una Base de Datos Distribuida? (Explicación Sencilla)](#2-qué-es-una-base-de-datos-distribuida-explicación-sencilla)
3. [El Cambio: De PostgreSQL (`Hobbies/`) a CockroachDB (`PruebasDistribuidas/`)](#3-el-cambio-de-postgresql-hobbies-a-cockroachdb-pruebasdistribuidas)
4. [¿Cómo funciona CockroachDB por dentro? (Conceptos Clave)](#4-cómo-funciona-cockroachdb-por-dentro-conceptos-clave)
5. [Paso a Paso: Cómo Montar y Usar la Base de Datos](#5-paso-a-paso-cómo-montar-y-usar-la-base-de-datos)
6. [Dataset Masivo de Prueba (500 Registros por Tabla y CSVs)](#6-dataset-masivo-de-prueba-500-registros-por-tabla-y-csvs)
7. [Consola Web de Monitoreo (Admin UI)](#7-consola-web-de-monitoreo-admin-ui)
8. [Experimento en Vivo: Prueba de Tolerancia a Fallos (Matar un Nodo)](#8-experimento-en-vivo-prueba-de-tolerancia-a-fallos-matar-un-nodo)
9. [Comandos de Referencia Rápida](#9-comandos-de-referencia-rápida)

---

## 1. ¿Servía el Docker que tenías? ¿Qué le faltaba?

**Sí, tu Docker sí servía en un 95%**, pero tenía un detalle crucial que impedía usarlo:

### El Problema:
En `docker-compose.yml` tenías definidos 3 nodos (`roach1`, `roach2`, `roach3`) que se buscaban entre sí mediante `--join=roach1:26357,roach2:26357,roach3:26357`. 

En CockroachDB, cuando se crea un clúster de múltiples máquinas por primera vez, **los nodos no empiezan a recibir conexiones hasta que reciben una orden de inicialización** (`cockroach init`). 
Como esa orden nunca se ejecutó, los 3 contenedores se quedaban esperando eternamente en un bucle:
> `Node will now attempt to join a running cluster, or wait for cockroach init.`

### La Solución que aplicamos:
1. Agregamos al `docker-compose.yml` un contenedor auxiliar (`cluster-init`) que envía automáticamente la orden de inicialización apenas arrancan los nodos.
2. Copiamos tu esquema y datos [Hobbies.sql](file:///Users/jhojan/Documents/Universidad/Semestre10/BasedeDatosDistribuidas/PruebasDistribuidas/Hobbies.sql) a esta carpeta.
3. Creamos el script automatizado [cargar_datos.sh](file:///Users/jhojan/Documents/Universidad/Semestre10/BasedeDatosDistribuidas/PruebasDistribuidas/cargar_datos.sh) para que con un solo comando crees la base de datos, las tablas y cargues los registros.

---

## 2. ¿Qué es una Base de Datos Distribuida? (Explicación Sencilla)

Para entenderlo, usemos una analogía cotidiana:

```mermaid
flowchart TD
    subgraph Centralizada ["1. Base de Datos Centralizada (PostgreSQL tradicional en Hobbies/)"]
        Srv["Un Solo Servidor Físico / Contenedor"]
        DB[(Almacenamiento Local)]
        Srv --> DB
        Client1["Usuario"] --> Srv
        Client2["Usuario"] --> Srv
    end

    subgraph Distribuida ["2. Base de Datos Distribuida (CockroachDB en PruebasDistribuidas/)"]
        N1["Nodo 1 (roach1)"]
        N2["Nodo 2 (roach2)"]
        N3["Nodo 3 (roach3)"]
        N1 <-->|Consenso Raft| N2
        N2 <-->|Consenso Raft| N3
        N3 <-->|Consenso Raft| N1
        UserA["Usuario"] --> N1
        UserB["Usuario"] --> N2
    end
```

### La Analogía del Banco:
* **Base de datos tradicional (Centralizada):**
  Es como una sucursal con **un único cajero** que tiene el libro contable físico. Si ese cajero se enferma o la sucursal se queda sin luz, **el banco cierra por completo**. Si llegan 500 clientes al tiempo, la fila se vuelve lenta y la única solución es ponerle un escritorio más grande a ese único cajero (*Escalamiento Vertical*).

* **Base de datos distribuida (Clúster):**
  Es como tener **3 cajeros en paralelo** (`roach1`, `roach2`, `roach3`). Cada uno tiene una copia sincronizada del libro contable. 
  - Si un cliente le pide $100 al Cajero 1, los cajeros se comunican entre sí para registrar el retiro.
  - **Si el Cajero 1 se desmaya o se apaga, los Cajeros 2 y 3 siguen atendiendo normalmente sin perder un solo centavo de información** (*Tolerancia a fallos y Alta Disponibilidad*).
  - Si llegan miles de clientes, simplemente añades un Cajero 4, 5 o 6 (*Escalamiento Horizontal*).

---

## 3. El Cambio: De PostgreSQL (`Hobbies/`) a CockroachDB (`PruebasDistribuidas/`)

En la carpeta `Hobbies/` tenías un archivo `docker-compose.yml` con **PostgreSQL estándar** (puerto `5433`). 

¿Qué cambia al pasar a CockroachDB en `PruebasDistribuidas/`?

| Característica | PostgreSQL (`Hobbies/`) | CockroachDB (`PruebasDistribuidas/`) |
| :--- | :--- | :--- |
| **Arquitectura** | Monolítica (1 nodo centralizado) | Distribuida NewSQL (3 nodos independientes) |
| **Punto único de falla** | Sí (Si el contenedor cae, se detiene la BD) | No (Puede morir un nodo y el clúster sigue vivo) |
| **Lenguaje SQL** | SQL estándar | SQL estándar (dialecto PostgreSQL) |
| **Compatibilidad** | Nativo PostgreSQL | **100% compatible con protocolo y clientes PostgreSQL** |
| **Puertos de acceso** | Solo 1 puerto (`5433`) | **3 puertos distintos** (Nodo 1: `26257`, Nodo 2: `26258`, Nodo 3: `26259`) |
| **Consola Web de salud** | Requiere herramientas externas (pgAdmin) | **Consola Web nativa integrada** en `http://localhost:8080` |

> [!NOTE]
> **¿Por qué funcionó tu script `Hobbies.sql` sin cambiarle nada?**
> Porque CockroachDB es un motor **NewSQL**: adopta la sintaxis y el protocolo de red de PostgreSQL, pero por debajo almacena y coordina los datos de forma distribuida. No tuviste que aprender una sintaxis rara ni renunciar a tus llaves foráneas (`FOREIGN KEY`) ni a tus `JOIN`.

---

## 4. ¿Cómo funciona CockroachDB por dentro? (Conceptos Clave)

### 1. Nodos (*Nodes*)
Cada contenedor (`roach1`, `roach2`, `roach3`) es un nodo del clúster. Todos los nodos son iguales; **no hay un "nodo maestro" ni un "esclavo"**. Puedes conectarte a cualquiera de ellos para leer o escribir.

### 2. Particionamiento por Rangos (*Ranges / Shards*)
CockroachDB divide tus tablas (`ESTUDIANTE`, `HOBBY`, `REALIZACION_HOBBY`, etc.) en bloques continuos de datos ordenados por su Llave Primaria llamados **Rangos** (por defecto de ~64 MB). Si tu tabla crece mucho, automáticamente se divide en más rangos y se reparten entre las máquinas.

### 3. Replicación y Algoritmo de Consenso (Raft & Quórum)
Cada Rango no se guarda en una sola máquina: **se replica 3 veces** (una copia en `roach1`, una en `roach2` y una en `roach3`).
- Cuando haces un `INSERT`: CockroachDB usa el protocolo **Raft**. Para confirmar que el dato se guardó, necesita que la **mayoría estricta (Quórum)** confirme la escritura.
- En un clúster de 3 nodos, la mayoría es: $\lfloor 3 / 2 \rfloor + 1 = \mathbf{2 \text{ nodos}}$.
- Por tanto, basta con que 2 nodos estén vivos para que todo el sistema funcione a la perfección.

### 4. Enrutamiento Inteligente
Si te conectas a `roach1` y pides un dato que físicamente está almacenado en el disco de `roach3`, tú no tienes que saberlo: `roach1` le pide el dato a `roach3` internamente a través de la red interna y te lo entrega como si estuviera en su propia memoria.

---

## 5. Paso a Paso: Cómo Montar y Usar la Base de Datos

### Paso 1: Levantar el Clúster
Desde esta carpeta (`PruebasDistribuidas/`), ejecuta en tu terminal:

```bash
docker compose up -d
```

Verás que se levantan:
- `roach1`: Nodo 1 (Puerto SQL: `26257`, Web UI: `8080`)
- `roach2`: Nodo 2 (Puerto SQL: `26258`, Web UI: `8081`)
- `roach3`: Nodo 3 (Puerto SQL: `26259`, Web UI: `8082`)
- `roach-init`: Contenedor que inicializa el clúster y luego se apaga pacíficamente.

Para comprobar que los 3 nodos están vivos:
```bash
docker exec -i roach1 ./cockroach node status --insecure --host=roach1:26257
```

---

### Paso 2: Cargar tu Base de Datos en el Clúster
Hemos preparado un único script ejecutable que hace todo el proceso de forma automática:

```bash
./cargar_datos.sh
```

El script se encarga de:
1. Crear la base de datos `hobbies` si no existe.
2. Cargar las tablas y los 500 registros por tabla desde [cargar_500_datos.sql](file:///Users/jhojan/Documents/Universidad/Semestre10/BasedeDatosDistribuidas/PruebasDistribuidas/cargar_500_datos.sql) (o el esquema inicial ligero con `./cargar_datos.sh Hobbies.sql`).
3. Mostrar el conteo final de filas de las 5 tablas para validar la carga.

---

### Paso 3: Probar las Consultas SQL
Puedes ejecutar las mismas 16 consultas de [consultas.sql](file:///Users/jhojan/Documents/Universidad/Semestre10/BasedeDatosDistribuidas/PruebasDistribuidas/consultas.sql) contra el clúster con este comando:

```bash
docker exec -i roach1 ./cockroach sql --insecure --host=roach1:26257 --database=hobbies < consultas.sql
```

O abrir una terminal SQL interactiva dentro de cualquier nodo:

```bash
# Conectarse interactivamente a roach1:
docker exec -it roach1 ./cockroach sql --insecure --host=roach1:26257 --database=hobbies

# O conectarse a roach2:
docker exec -it roach2 ./cockroach sql --insecure --host=roach2:26257 --database=hobbies
```

Dentro de la terminal puedes escribir cualquier SQL:
```sql
SELECT * FROM ESTUDIANTE;
SELECT e.NOMBRE, h.NOMBRE AS HOBBY FROM ESTUDIANTE e JOIN ESTUDIANTE_HOBBY eh ON eh.ESTUDIANTE_ID = e.ID JOIN HOBBY h ON h.ID = eh.HOBBY_ID;
```

---

### Paso 4: Conectarte desde un Gestor Visual (DBeaver, TablePlus, DataGrip, VS Code)
CockroachDB habla el mismo protocolo que PostgreSQL, por lo que en tu cliente gráfico favorito eliges **PostgreSQL** con estos datos:

- **Host:** `localhost` (o `127.0.0.1`)
- **Port:** `26257` (Nodo 1) o `26258` (Nodo 2) o `26259` (Nodo 3)
- **Database:** `hobbies`
- **User:** `root`
- **Password:** *(dejar vacío, no tiene contraseña)*
- **SSL:** `Disable` / Desactivado (modo insecure)

---

## 6. Dataset Masivo de Prueba (500 Registros por Tabla y CSVs)

Para evaluar el comportamiento, particionamiento y rendimiento del clúster distribuido, se generaron **500 registros por cada una de las 5 tablas**, asegurando integridad referencial estricta (llaves primarias, foráneas compuestas y pares únicos).

### Archivos CSV Generados:
Todos los archivos se encuentran disponibles en la carpeta [`datos_csv/`](file:///Users/jhojan/Documents/Universidad/Semestre10/BasedeDatosDistribuidas/PruebasDistribuidas/datos_csv/):

| Tabla | Archivo CSV | Registros | Descripción de Campos |
| :--- | :--- | :--- | :--- |
| `ESTUDIANTE` | [`estudiante.csv`](file:///Users/jhojan/Documents/Universidad/Semestre10/BasedeDatosDistribuidas/PruebasDistribuidas/datos_csv/estudiante.csv) | 500 filas | `id`, `nombre` (nombres y apellidos reales), `edad` (18-32), `correo_electronico` |
| `HOBBY` | [`hobby.csv`](file:///Users/jhojan/Documents/Universidad/Semestre10/BasedeDatosDistribuidas/PruebasDistribuidas/datos_csv/hobby.csv) | 500 filas | `id`, `nombre` (deportes, artes, música, tecnología, etc.) |
| `RECOMPENSA` | [`recompensa.csv`](file:///Users/jhojan/Documents/Universidad/Semestre10/BasedeDatosDistribuidas/PruebasDistribuidas/datos_csv/recompensa.csv) | 500 filas | `id`, `nombre` (bonos, descuentos, insignias, becas), `valor` (10 a 500) |
| `ESTUDIANTE_HOBBY` | [`estudiante_hobby.csv`](file:///Users/jhojan/Documents/Universidad/Semestre10/BasedeDatosDistribuidas/PruebasDistribuidas/datos_csv/estudiante_hobby.csv) | 500 filas | `estudiante_id`, `hobby_id` (pares únicos validados) |
| `REALIZACION_HOBBY` | [`realizacion_hobby.csv`](file:///Users/jhojan/Documents/Universidad/Semestre10/BasedeDatosDistribuidas/PruebasDistribuidas/datos_csv/realizacion_hobby.csv) | 500 filas | `id`, `estudiante_id`, `hobby_id`, `recompensa_id`, `fecha` (fechas del 2026) |

---

### 💡 Observación Clave: ¿Por qué usamos un `.sql` en vez de cargar directamente los `.csv` con SQL puro en CockroachDB?

Es muy natural preguntarse: *¿Por qué no simplemente ejecutar un comando SQL que lea los archivos `.csv` en vez de generar un archivo `.sql`?*

La respuesta se debe a la arquitectura interna y el modelo de licenciamiento de **CockroachDB**:

1. **`IMPORT INTO` es una característica Enterprise (comercial):** En CockroachDB nativo, el comando para ingesta masiva de archivos CSV es `IMPORT INTO`, pero está clasificado como función Enterprise (requiere licencia de pago).
2. **Almacenamiento remoto:** CockroachDB está diseñado para clústeres en la nube donde los nodos corren en servidores físicos diferentes. Por ello, `IMPORT INTO` no busca un archivo en la ruta local de tu computadora, sino que espera una URL de almacenamiento distribuido en red (como Amazon S3, Google Cloud Storage, Azure Blob o un servidor HTTP interno).
3. **Contenedores Docker mínimos:** Los contenedores oficiales de CockroachDB solo incluyen el binario del motor distribuido; no traen clientes adicionales para parsear archivos locales externos.

> [!NOTE]
> **Conclusión técnica:** Para un entorno de desarrollo o académico donde trabajamos con la versión gratuita y 100% contenida en Docker, el archivo [cargar_500_datos.sql](file:///Users/jhojan/Documents/Universidad/Semestre10/BasedeDatosDistribuidas/PruebasDistribuidas/cargar_500_datos.sql) es el estándar universal: se ejecuta a través del protocolo SQL estándar sin requerir licencias de pago, sin dependencias externas y cargando los datos en segundos dentro de Docker.
>
> *(Nota adicional)*: Como CockroachDB es compatible a nivel de red con PostgreSQL, herramientas cliente externas como `psql` pueden transferir CSVs con el comando cliente `\copy`, pero requieren tener PostgreSQL instalado localmente en el host. Para mantener el proyecto completamente autónomo y funcional únicamente con Docker, centralizamos la carga en el script unificado.

---

### Cómo Cargar los Datos al Clúster:
Solo necesitas ejecutar el único script unificado:

```bash
./cargar_datos.sh
```

El script se encarga de:
1. Verificar que la base de datos `hobbies` exista en el clúster.
2. Ejecutar [cargar_500_datos.sql](file:///Users/jhojan/Documents/Universidad/Semestre10/BasedeDatosDistribuidas/PruebasDistribuidas/cargar_500_datos.sql) para cargar los 500 registros por tabla.
3. Imprimir el conteo de filas de las 5 tablas para validar la carga.

*(Opcional - Si quieres cargar el dataset inicial de 6 filas)*:
```bash
./cargar_datos.sh Hobbies.sql
```

*(Opcional - Si deseas regenerar los archivos CSV y SQL)*:
```bash
python3 generate_dataset.py
```

---

## 7. Consola Web de Monitoreo (Admin UI)

CockroachDB incluye una consola web muy completa para ver la salud del clúster en tiempo real:

👉 Abre en tu navegador: **[http://localhost:8080](http://localhost:8080)**

¿Qué vas a encontrar allí?
1. **Cluster Overview:** Verás los 3 nodos con puntos verdes indicando que están sanos (*Healthy*).
2. **Databases:** Verás la base de datos `hobbies` con sus tablas y tamaño (verás reflejadas las 500 filas por tabla).
3. **Metrics:** Gráficas de CPU, memoria, operaciones de lectura/escritura por segundo y latencia.
4. **Statements:** Lista de consultas ejecutadas recientemente y su tiempo de respuesta.

---

## 8. Experimento en Vivo: Prueba de Tolerancia a Fallos (Matar un Nodo)

Esta es la mejor prueba práctica para que veas en acción el poder de una base de datos distribuida frente a una tradicional:

```mermaid
sequenceDiagram
    autonumber
    actor Tu as Terminal / Usuario
    participant N1 as Nodo 1 (roach1)
    participant N2 as Nodo 2 (roach2)
    participant N3 as Nodo 3 (roach3)

    Tu->>N1: Consulta SELECT * FROM ESTUDIANTE
    N1-->>Tu: Devuelve los 3 estudiantes
    Note over N1: ¡Apagamos Nodo 1! (docker stop roach1)
    Tu->>N2: Consulta SELECT * FROM ESTUDIANTE (por puerto 26258)
    Note over N2,N3: Nodos 2 y 3 tienen Quórum (2 de 3)
    N2-->>Tu: ¡Devuelve los mismos datos sin errores!
    Note over N1: Reiniciamos Nodo 1 (docker start roach1)
    Note over N1,N3: Nodo 1 se reincorpora y sincroniza automáticamente
```

### Pasos para replicar el experimento:

1. **Haz una consulta al Nodo 2 (puerto 26258):**
   ```bash
   docker exec -i roach2 ./cockroach sql --insecure --host=roach2:26257 --database=hobbies -e "SELECT NOMBRE FROM ESTUDIANTE;"
   ```
   *Resultado:* Verás a Ana, Luis y Sofía.

2. **Simula una catástrofe apagando el Nodo 1:**
   ```bash
   docker stop roach1
   ```

3. **Vuelve a hacer la consulta al Nodo 2 o al Nodo 3:**
   ```bash
   docker exec -i roach2 ./cockroach sql --insecure --host=roach2:26257 --database=hobbies -e "SELECT NOMBRE FROM ESTUDIANTE;"
   ```
   *Resultado:* **¡La base de datos sigue respondiendo al 100%!** No perdiste datos ni se cayó el servicio.

4. **Revisa la consola web:**
   Abre [http://localhost:8081](http://localhost:8081) (consola web del Nodo 2). Verás que reporta 1 nodo como *Dead / Suspect*, pero el clúster sigue operativo.

5. **Revive el Nodo 1:**
   ```bash
   docker start roach1
   ```
   El Nodo 1 se reintegrará automáticamente y recibirá las actualizaciones pendientes mediante Raft sin intervención manual.

---

## 9. Comandos de Referencia Rápida

| Acción | Comando |
| :--- | :--- |
| Iniciar clúster | `docker compose up -d` |
| Detener clúster | `docker compose stop` |
| Apagar y borrar contenedores | `docker compose down` |
| Borrar todo (incluyendo datos del disco) | `docker compose down -v` |
| Ver estado de los nodos | `docker exec -i roach1 ./cockroach node status --insecure --host=roach1:26257` |
| Cargar dataset masivo (500 registros por tabla) | `./cargar_datos.sh` |
| Cargar dataset inicial alternativo (6 registros) | `./cargar_datos.sh Hobbies.sql` |
| Regenerar CSVs y SQL de 500 registros | `python3 generate_dataset.py` |
| Entrar a la consola SQL | `docker exec -it roach1 ./cockroach sql --insecure --host=roach1:26257 --database=hobbies` |
| Ejecutar consultas.sql | `docker exec -i roach1 ./cockroach sql --insecure --host=roach1:26257 --database=hobbies < consultas.sql` |

