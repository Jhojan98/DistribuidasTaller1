#!/usr/bin/env python3
"""
Generador del dataset de prueba para el cluster CockroachDB (base 'hobbies').

Crea los CSV de datos_csv/ y el script cargar_datos.sql con una
distribucion equilibrada:

  - Cada estudiante tiene VARIOS hobbies y VARIAS realizaciones.
  - Cada hobby y cada recompensa se usa casi el mismo numero de veces
    (ninguno queda sin usar; la diferencia entre el mas y el menos usado
    es de solo 1-2 unidades).
  - Toda realizacion referencia un par (estudiante, hobby) que existe en
    ESTUDIANTE_HOBBY: la integridad referencial se garantiza por
    construccion y se verifica antes de escribir los archivos.

Para cambiar cantidades, rangos o fechas edita CONFIG y ejecuta:
    python generate_dataset.py
La guia completa esta en README.md, seccion 10.
"""
import csv
import os
import random
from collections import Counter
from datetime import date, timedelta

# ----------------------------------------------------------------
# CONFIGURACION: edita estos valores para alterar el dataset.
# Ver README.md seccion 10 para ejemplos concretos.
# ----------------------------------------------------------------
CONFIG = {
    # Misma semilla => exactamente los mismos datos (reproducible).
    "semilla": 42,

    # Tamanos de las tablas principales.
    "num_estudiantes": 500,
    "num_hobbies": 250,
    "num_recompensas": 250,

    # Hobbies y realizaciones POR ESTUDIANTE (minimo, maximo).
    # El total de filas de ESTUDIANTE_HOBBY y REALIZACION_HOBBY es la
    # suma de lo que salga por estudiante (~2000 con estos rangos).
    "hobbies_por_estudiante": (2, 6),
    "realizaciones_por_estudiante": (2, 6),

    # Rango de fechas de REALIZACION_HOBBY y rangos de edad/valor.
    "fecha_inicio": date(2026, 1, 1),
    "fecha_fin": date(2026, 10, 24),
    "edad_min": 18,
    "edad_max": 32,
    "valor_min": 10,
    "valor_max": 500,
}

random.seed(CONFIG["semilla"])

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_DIR = os.path.join(BASE_DIR, "datos_csv")
SQL_FILE = os.path.join(BASE_DIR, "cargar_datos.sql")

os.makedirs(CSV_DIR, exist_ok=True)

# 1. Nombres y Apellidos para Estudiantes
nombres = [
    "Alejandro", "Sofia", "Mateo", "Valentina", "Sebastian", "Camila", "Nicolas", "Isabella",
    "Santiago", "Mariana", "Lucas", "Lucia", "Diego", "Gabriela", "Daniel", "Catalina",
    "Samuel", "Daniela", "Joaquin", "Valeria", "Tomas", "Paula", "Martin", "Elena",
    "Felipe", "Andrea", "Emilio", "Sara", "Andres", "Juana", "Julian", "Clara",
    "David", "Victoria", "Gabriel", "Laura", "Esteban", "Natalia", "Carlos", "Juliana",
    "Manuel", "Maria", "Simon", "Ana", "Pablo", "Carolina", "Leonardo", "Fernanda",
    "Ricardo", "Luisa"
]

apellidos = [
    "Gomez", "Rodriguez", "Lopez", "Garcia", "Martinez", "Perez", "Gonzalez", "Sanchez",
    "Ramirez", "Torres", "Flores", "Diaz", "Vargas", "Castro", "Morales", "Alvarez",
    "Mendoza", "Rojas", "Jimenez", "Ortiz", "Silva", "Hernandez", "Ruiz", "Gutierrez",
    "Suarez", "Navarro", "Acosta", "Rios", "Medina", "Castillo", "Cabrera", "Vega",
    "Munoz", "Pena", "Guerrero", "Cortes", "Pacheco", "Reyes", "Cardona", "Duque",
    "Herrera", "Montes", "Quintero", "Rendon", "Salazar", "Zapata", "Velasquez", "Mejia",
    "Restrepo", "Ospina"
]

# Actividades y modalidades: los hobbies se generan combinando ambas
# listas (50 x 10 = 500 combinaciones posibles) hasta llenar num_hobbies.
actividades = [
    "Futbol", "Baloncesto", "Voleibol", "Natacion", "Ajedrez", "Ciclismo", "Senderismo",
    "Atletismo", "Tenis de campo", "Tenis de mesa", "Pintura al oleo", "Acuarela",
    "Dibujo digital", "Escultura", "Fotografia urbana", "Fotografia de naturaleza",
    "Guitarra acustica", "Guitarra electrica", "Piano", "Bateria", "Bajo electrico",
    "Canto coral", "Produccion musical", "Lectura de ciencia ficcion", "Lectura de historia",
    "Escritura creativa", "Poesia", "Programacion en Python", "Desarrollo web",
    "Robotica educativa", "Modelado 3D", "Animacion digital", "Videojuegos de estrategia",
    "Videojuegos de rol", "Juegos de mesa", "Cocina italiana", "Reposteria artesanal",
    "Cocteleria sin alcohol", "Barismo y cafe", "Jardineria urbana", "Bonsai", "Yoga",
    "Meditacion guiada", "Calistenia", "Crossfit", "Artes marciales", "Teatro callejero",
    "Danza contemporanea", "Salsa y bachata", "Origami y papiroflexia"
]

modalidades = [
    "Nivel Principiante", "Nivel Intermedio", "Nivel Avanzado", "En Grupo", "Al Aire Libre",
    "En Laboratorio", "Taller Intensivo", "Modalidad Nocturna", "De Fin de Semana",
    "Club Competitivo"
]

tipos_recompensa = [
    "Bono Cafeteria", "Descuento Libreria", "Puntos Bienestar", "Insignia Deportiva",
    "Acceso Gimnasio", "Bono Almuerzo", "Kit Papeleria", "Entrada Cine Cultural",
    "Certificado Excelencia", "Bono Tienda Universitaria"
]

# ----------------------------------------------------------------
# Helpers de reparto equilibrado
# ----------------------------------------------------------------

def repartir_sin_repetidos(ids, necesidades):
    """Reparte unidades de `ids` entre sujetos de forma balanceada.

    necesidades: lista de (sujeto, cantidad). En cada eleccion solo se
    consideran los ids menos usados hasta ese momento (con desempate
    aleatorio), asi cada id termina usado casi el mismo numero de veces
    (diferencia maxima de 1-2 usos) y un sujeto nunca recibe repetidos.
    """
    ids = list(ids)
    uso = {i: 0 for i in ids}
    resultado = {}
    for sujeto, cantidad in necesidades:
        cantidad = min(cantidad, len(ids))
        ordenados = sorted(ids, key=lambda i: (uso[i], random.random()))
        elegidos = set(ordenados[:cantidad])
        for i in elegidos:
            uso[i] += 1
        resultado[sujeto] = elegidos
    return resultado


def repartidor_ciclico(ids):
    """Iterador infinito que entrega los ids barajados en pasadas completas.

    Con N entregas cada id se usa N/len(ids) veces exactas: balance
    perfecto para columnas que si admiten repeticion.
    """
    while True:
        pool = list(ids)
        random.shuffle(pool)
        for valor in pool:
            yield valor


# ----------------------------------------------------------------
# 1. Estudiantes
# ----------------------------------------------------------------
estudiantes = []
for i in range(1, CONFIG["num_estudiantes"] + 1):
    nom = nombres[(i - 1) % len(nombres)]
    ape1 = apellidos[((i - 1) // len(nombres)) % len(apellidos)]
    ape2 = apellidos[(i * 3) % len(apellidos)]
    edad = random.randint(CONFIG["edad_min"], CONFIG["edad_max"])
    # correo normalizado sin tildes ni espacios; el id lo hace unico
    correo = f"{nom.lower()}.{ape1.lower()}{i}@universidad.edu.co"
    estudiantes.append({
        "id": i,
        "nombre": f"{nom} {ape1} {ape2}",
        "edad": edad,
        "correo_electronico": correo
    })

# ----------------------------------------------------------------
# 2. Hobbies (actividad x modalidad, rotando ambas listas)
# ----------------------------------------------------------------
hobbies = []
combo = 0
while len(hobbies) < CONFIG["num_hobbies"]:
    act = actividades[combo % len(actividades)]
    mod = modalidades[(combo // len(actividades)) % len(modalidades)]
    hobbies.append({"id": len(hobbies) + 1, "nombre": f"{act} ({mod})"})
    combo += 1

# ----------------------------------------------------------------
# 3. Recompensas (tipo x nivel, rotando la lista de tipos)
# ----------------------------------------------------------------
recompensas = []
for i in range(1, CONFIG["num_recompensas"] + 1):
    tipo = tipos_recompensa[(i - 1) % len(tipos_recompensa)]
    nivel = ((i - 1) // len(tipos_recompensa)) + 1
    recompensas.append({
        "id": i,
        "nombre": f"{tipo} - Nivel {nivel}",
        "valor": random.randint(CONFIG["valor_min"], CONFIG["valor_max"])
    })

# ----------------------------------------------------------------
# 4. Estudiante_Hobby: varios hobbies por estudiante, balanceado
# ----------------------------------------------------------------
h_min, h_max = CONFIG["hobbies_por_estudiante"]
necesidades_h = [(e["id"], random.randint(h_min, h_max)) for e in estudiantes]
hobbies_de = repartir_sin_repetidos([h["id"] for h in hobbies], necesidades_h)

estudiante_hobbies = []
for e in estudiantes:
    for h_id in sorted(hobbies_de[e["id"]]):
        estudiante_hobbies.append({
            "estudiante_id": e["id"],
            "hobby_id": h_id
        })

# ----------------------------------------------------------------
# 5. Realizacion_Hobby: varias realizaciones por estudiante
#    Cada una usa un par (estudiante, hobby) que si existe.
# ----------------------------------------------------------------
r_min, r_max = CONFIG["realizaciones_por_estudiante"]
fecha_inicio = CONFIG["fecha_inicio"]
total_dias = (CONFIG["fecha_fin"] - fecha_inicio).days
siguiente_recompensa = repartidor_ciclico([r["id"] for r in recompensas])

filas = []
for e in estudiantes:
    mis_hobbies = sorted(hobbies_de[e["id"]])
    for _ in range(random.randint(r_min, r_max)):
        filas.append({
            "estudiante_id": e["id"],
            "hobby_id": random.choice(mis_hobbies),
            "recompensa_id": next(siguiente_recompensa),
            "fecha": (fecha_inicio + timedelta(days=random.randint(0, total_dias))).strftime("%Y-%m-%d")
        })

# Se barajan y luego se numeran para que los IDs no queden agrupados
# por estudiante ni por fecha.
random.shuffle(filas)
realizaciones = [{"id": i, **f} for i, f in enumerate(filas, start=1)]

# ----------------------------------------------------------------
# Verificacion de integridad antes de escribir nada
# ----------------------------------------------------------------
pares = {(p["estudiante_id"], p["hobby_id"]) for p in estudiante_hobbies}
assert len(estudiante_hobbies) == len(pares), "Pares duplicados en ESTUDIANTE_HOBBY"
assert all((r["estudiante_id"], r["hobby_id"]) in pares for r in realizaciones), \
    "Realizacion con par (estudiante, hobby) inexistente"
assert len({r["id"] for r in realizaciones}) == len(realizaciones), "IDs duplicados"

# ----------------- ESCRIBIR CSVs -----------------

with open(os.path.join(CSV_DIR, "estudiante.csv"), "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "nombre", "edad", "correo_electronico"])
    writer.writeheader()
    writer.writerows(estudiantes)

with open(os.path.join(CSV_DIR, "hobby.csv"), "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "nombre"])
    writer.writeheader()
    writer.writerows(hobbies)

with open(os.path.join(CSV_DIR, "recompensa.csv"), "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "nombre", "valor"])
    writer.writeheader()
    writer.writerows(recompensas)

with open(os.path.join(CSV_DIR, "estudiante_hobby.csv"), "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["estudiante_id", "hobby_id"])
    writer.writeheader()
    writer.writerows(estudiante_hobbies)

with open(os.path.join(CSV_DIR, "realizacion_hobby.csv"), "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "estudiante_id", "hobby_id", "recompensa_id", "fecha"])
    writer.writeheader()
    writer.writerows(realizaciones)

print(f"CSVs creados exitosamente en {CSV_DIR}")

# ----------------- ESCRIBIR SQL -----------------

def escape_sql(val):
    if isinstance(val, str):
        return "'" + val.replace("'", "''") + "'"
    return str(val)

with open(SQL_FILE, "w", encoding="utf-8") as f:
    f.write("-- ============================================================\n")
    f.write("-- CARGA DE DATOS PARA EL CLUSTER COCKROACHDB\n")
    f.write("-- Base de datos: hobbies\n")
    f.write(f"--   ESTUDIANTE: {len(estudiantes)} filas\n")
    f.write(f"--   HOBBY: {len(hobbies)} filas\n")
    f.write(f"--   RECOMPENSA: {len(recompensas)} filas\n")
    f.write(f"--   ESTUDIANTE_HOBBY: {len(estudiante_hobbies)} filas\n")
    f.write(f"--   REALIZACION_HOBBY: {len(realizaciones)} filas\n")
    f.write(f"-- Generado por generate_dataset.py (semilla={CONFIG['semilla']})\n")
    f.write("-- ============================================================\n\n")

    f.write("-- 1. Limpieza de tablas (preservando o recreando esquema)\n")
    f.write("DROP TABLE IF EXISTS REALIZACION_HOBBY, ESTUDIANTE_HOBBY, ESTUDIANTE, HOBBY, RECOMPENSA CASCADE;\n\n")

    f.write("CREATE TABLE ESTUDIANTE (\n")
    f.write("    ID INT PRIMARY KEY,\n")
    f.write("    NOMBRE VARCHAR(100),\n")
    f.write("    EDAD INT,\n")
    f.write("    CORREO_ELECTRONICO VARCHAR(100)\n")
    f.write(");\n\n")

    f.write("CREATE TABLE HOBBY (\n")
    f.write("    ID INT PRIMARY KEY,\n")
    f.write("    NOMBRE VARCHAR(100)\n")
    f.write(");\n\n")

    f.write("CREATE TABLE ESTUDIANTE_HOBBY (\n")
    f.write("    ESTUDIANTE_ID INT,\n")
    f.write("    HOBBY_ID INT,\n")
    f.write("    PRIMARY KEY (ESTUDIANTE_ID, HOBBY_ID),\n")
    f.write("    FOREIGN KEY (ESTUDIANTE_ID) REFERENCES ESTUDIANTE(ID),\n")
    f.write("    FOREIGN KEY (HOBBY_ID) REFERENCES HOBBY(ID)\n")
    f.write(");\n\n")

    f.write("CREATE TABLE RECOMPENSA (\n")
    f.write("    ID INT PRIMARY KEY,\n")
    f.write("    NOMBRE VARCHAR(100),\n")
    f.write("    VALOR INT\n")
    f.write(");\n\n")

    f.write("CREATE TABLE REALIZACION_HOBBY (\n")
    f.write("    ID INT PRIMARY KEY,\n")
    f.write("    ESTUDIANTE_ID INT,\n")
    f.write("    HOBBY_ID INT,\n")
    f.write("    RECOMPENSA_ID INT,\n")
    f.write("    FECHA DATE,\n")
    f.write("    FOREIGN KEY (ESTUDIANTE_ID, HOBBY_ID)\n")
    f.write("        REFERENCES ESTUDIANTE_HOBBY(ESTUDIANTE_ID, HOBBY_ID),\n")
    f.write("    FOREIGN KEY (RECOMPENSA_ID) REFERENCES RECOMPENSA(ID)\n")
    f.write(");\n\n")

    chunk_size = 100

    def escribir_inserts(tabla, columnas, filas_tabla, formato_fila, comentario):
        f.write(comentario)
        for c in range(0, len(filas_tabla), chunk_size):
            chunk = filas_tabla[c:c+chunk_size]
            vals = ",\n".join(formato_fila(fila) for fila in chunk)
            f.write(f"INSERT INTO {tabla} ({', '.join(columnas)}) VALUES\n{vals};\n\n")

    escribir_inserts(
        "ESTUDIANTE", ["ID", "NOMBRE", "EDAD", "CORREO_ELECTRONICO"], estudiantes,
        lambda e: f"({e['id']}, {escape_sql(e['nombre'])}, {e['edad']}, {escape_sql(e['correo_electronico'])})",
        f"-- 2. Insercion de {len(estudiantes)} ESTUDIANTES\n")

    escribir_inserts(
        "HOBBY", ["ID", "NOMBRE"], hobbies,
        lambda h: f"({h['id']}, {escape_sql(h['nombre'])})",
        f"-- 3. Insercion de {len(hobbies)} HOBBIES\n")

    escribir_inserts(
        "RECOMPENSA", ["ID", "NOMBRE", "VALOR"], recompensas,
        lambda r: f"({r['id']}, {escape_sql(r['nombre'])}, {r['valor']})",
        f"-- 4. Insercion de {len(recompensas)} RECOMPENSAS\n")

    escribir_inserts(
        "ESTUDIANTE_HOBBY", ["ESTUDIANTE_ID", "HOBBY_ID"], estudiante_hobbies,
        lambda p: f"({p['estudiante_id']}, {p['hobby_id']})",
        f"-- 5. Insercion de {len(estudiante_hobbies)} ESTUDIANTE_HOBBY\n")

    escribir_inserts(
        "REALIZACION_HOBBY", ["ID", "ESTUDIANTE_ID", "HOBBY_ID", "RECOMPENSA_ID", "FECHA"], realizaciones,
        lambda r: f"({r['id']}, {r['estudiante_id']}, {r['hobby_id']}, {r['recompensa_id']}, '{r['fecha']}')",
        f"-- 6. Insercion de {len(realizaciones)} REALIZACION_HOBBY\n")

print(f"SQL generado exitosamente en {SQL_FILE}")

# ----------------- RESUMEN DE DISTRIBUCION -----------------
hobb_por_alumno = Counter(p["estudiante_id"] for p in estudiante_hobbies)
uso_hobby = Counter(p["hobby_id"] for p in estudiante_hobbies)
real_por_alumno = Counter(r["estudiante_id"] for r in realizaciones)
uso_recompensa = Counter(r["recompensa_id"] for r in realizaciones)

print()
print("=" * 62)
print("RESUMEN DEL DATASET GENERADO")
print("=" * 62)
print(f"ESTUDIANTE        {len(estudiantes):>6} filas")
print(f"HOBBY             {len(hobbies):>6} filas")
print(f"RECOMPENSA        {len(recompensas):>6} filas")
print(f"ESTUDIANTE_HOBBY  {len(estudiante_hobbies):>6} filas | "
      f"hobbies/estudiante: {min(hobb_por_alumno.values())}-{max(hobb_por_alumno.values())} | "
      f"uso de cada hobby: {min(uso_hobby.values())}-{max(uso_hobby.values())}")
print(f"REALIZACION       {len(realizaciones):>6} filas | "
      f"realizaciones/estudiante: {min(real_por_alumno.values())}-{max(real_por_alumno.values())} | "
      f"uso de cada recompensa: {min(uso_recompensa.values())}-{max(uso_recompensa.values())}")
print("=" * 62)
