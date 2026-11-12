#!/usr/bin/env python3
"""
Generador del dataset de prueba para el cluster CockroachDB (base 'hobbies').

Crea los CSV de datos_csv/ y el script cargar_datos.sql con una
distribucion equilibrada:

  - 40 hobbies fijos y 40 recompensas (una por hobby), sin replicacion.
  - Cada estudiante tiene un CODIGO unico de 11 digitos:
        anio(4) + semestre(1) + codigo de carrera(3) + consecutivo(3)
    por ejemplo: 20221020098, 20152050140, 20201090069.
  - Cada estudiante tiene VARIAS realizaciones (2 a 6) y el dataset
    cierra en exactamente `total_realizaciones` filas.
  - Cada realizacion otorga la recompensa que corresponde a su hobby
    (la recompensa N es la del hobby N).

Para cambiar cantidades, rangos o fechas edita CONFIG y ejecuta:
    python generate_dataset.py
La guia completa esta en README.md.
"""
import csv
import os
import random
from collections import Counter
from datetime import date, timedelta

# ----------------------------------------------------------------
# CONFIGURACION: edita estos valores para alterar el dataset.
# Ver README.md para mas detalles.
# ----------------------------------------------------------------
CONFIG = {
    # Misma semilla => exactamente los mismos datos (reproducible).
    "semilla": 42,

    # Tamanos de las tablas principales.
    # HOBBY y RECOMPENSA salen de las listas fijas de abajo (40 c/u).
    "num_estudiantes": 500,
    "total_realizaciones": 2000,

    # Realizaciones POR ESTUDIANTE (minimo, maximo). El reparto se
    # ajusta solo hasta cerrar en total_realizaciones exactas.
    "realizaciones_por_estudiante": (2, 6),

    # Hobbies distintos que practica cada estudiante (solo se usa para
    # generar las realizaciones; la tabla ESTUDIANTE_HOBBY ya no existe).
    "hobbies_por_estudiante": (2, 6),

    # Rango de fechas de REALIZACION_HOBBY y rangos de edad/valor.
    "fecha_inicio": date(2026, 1, 1),
    "fecha_fin": date(2026, 11, 11),
    "edad_min": 18,
    "edad_max": 32,
    "valor_min": 10,
    "valor_max": 500,

    # Codigo de estudiante: anio(4) + semestre(1) + carrera(3) + consecutivo(3)
    "anio_min": 2000,
    "anio_max": 2026,
    "semestres": (1, 2),
    "carrera_min": 10,      # 010, 020, ... 090
    "carrera_max": 90,
    "carrera_paso": 10,
    "consecutivo_max": 200,  # 000 al 200
}

random.seed(CONFIG["semilla"])

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_DIR = os.path.join(BASE_DIR, "datos_csv")
SQL_FILE = os.path.join(BASE_DIR, "cargar_datos.sql")

os.makedirs(CSV_DIR, exist_ok=True)

# ----------------------------------------------------------------
# 1. Nombres y Apellidos para Estudiantes
# ----------------------------------------------------------------
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

# ----------------------------------------------------------------
# 2. Hobbies: lista fija de 40 (sin replicacion ni modalidades)
#    La posicion define el id: el hobby i es la recompensa i.
# ----------------------------------------------------------------
hobbies_nombres = [
    "Hacer serenatas a sordos",
    "Desayunar en las noches",
    "Despegar los stickers de Whatsapp",
    "Peluquear calvos",
    "Comprar dulces a cuotas",
    "Prestar servicio en las Farc",
    "Alquilar comida",
    "Apostar en carreras de caballos de mar",
    "Amarrar cordones umbilicales",
    "Madrugar a las 6 de la tarde",
    "Dar limosna con datáfono",
    "Planchar las arrugas de los viejitos",
    "Bautizar gatos",
    "Comer en puestos de comidas lentas",
    "Ir a piscina en la iglesia",
    "Embarazar abuelitas",
    "Lavar loza con guantes de boxeo",
    "Grabar fotos",
    "Hacer oficio",
    "Dar regalos en funerales",
    "Pagar peajes en cicla",
    "Pescar en volcanes",
    "Purificar agua con filtros de tik tok",
    "Coleccionar tréboles de mala suerte",
    "Pagar el bus e ir a pie",
    "Sacar a las perritas",
    "Dormir",
    "Donar a ancianatos de bebés",
    "Secar la ropa en agua",
    "Pedirle la silla a una embarazada",
    "Llevar calculadoras a exámenes de español",
    "Darle la bendición a ateos",
    "Lavar bicicletas en la lavadora",
    "Pagar 3 y llevar 2",
    "Ganarle el bingo a abuelitas",
    "Fumar emulsion de Scott",
    "Cepillarse con agua del inodoro",
    "Darle pizzas familiares a huerfanos",
    "Ir a la universidad con maletas de rueditas",
    "Contratar abogados para sacar las muelas del juicio",
]

# ----------------------------------------------------------------
# 3. Recompensas: 40, una por hobby (misma posicion = mismo id)
# ----------------------------------------------------------------
recompensas_nombres = [
    "instrumentos",
    "platos",
    "celular",
    "maquina de peluquear",
    "mas capacidad de cuotas",
    "mas armas",
    "mas comida",
    "caballos de mar con esteroides",
    "cordones umbilicales reforzados",
    "reloj sin manecillas",
    "datáfono con NFC",
    "crema antiarrugas",
    "agua bendita en bidón",
    "menú exprés",
    "ropa de piscina",
    "mas abuelitas",
    "guantes deluxe",
    "grabadora nueva",
    "mocos de diferentes sabores",
    "urnas decoradas",
    "casco con visera",
    "anzuelos a prueba de lava",
    "filtro verified",
    "tréboles de cuatro hojas",
    "abono de bus sin usar",
    "frascos de uñas",
    "tarro de chicles",
    "cunas con rueditas",
    "ropa ya seca",
    "silla con cojín",
    "calculadora con acentos",
    "mano con poderes",
    "lavadora con pedales",
    "3 facturas y 2 productos",
    "bolitas de bingo de oro",
    "emulsión con filtro",
    "cepillo con enjuague",
    "pizza con pepperoni doble",
    "maleta con rueditas nuevas",
    "muela de oro",
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


def generar_codigos(n):
    """Genera n CODIGOS unicos de estudiante de 11 digitos.

    Estructura: anio(4) + semestre(1) + codigo de carrera(3) + consecutivo(3)
    Ejemplos: 20221020098, 20152050140, 20201090069
    """
    anios = list(range(CONFIG["anio_min"], CONFIG["anio_max"] + 1))
    semestres = list(CONFIG["semestres"])
    carreras = list(range(CONFIG["carrera_min"], CONFIG["carrera_max"] + 1,
                          CONFIG["carrera_paso"]))
    consecutivos = list(range(CONFIG["consecutivo_max"] + 1))

    codigos = []
    usados = set()
    while len(codigos) < n:
        codigo = (
            f"{random.choice(anios)}"
            f"{random.choice(semestres)}"
            f"{random.choice(carreras):03d}"
            f"{random.choice(consecutivos):03d}"
        )
        if codigo not in usados:
            usados.add(codigo)
            codigos.append(codigo)
    return codigos


def repartir_realizaciones(n_estudiantes, total, r_min, r_max):
    """Asigna a cada estudiante un numero de realizaciones (r_min..r_max)
    de modo que la suma sea exactamente `total`."""
    conteos = [random.randint(r_min, r_max) for _ in range(n_estudiantes)]
    falta = total - sum(conteos)
    while falta != 0:
        i = random.randrange(n_estudiantes)
        if falta > 0 and conteos[i] < r_max:
            conteos[i] += 1
            falta -= 1
        elif falta < 0 and conteos[i] > r_min:
            conteos[i] -= 1
            falta += 1
    return conteos


# ----------------------------------------------------------------
# 1. Estudiantes (con CODIGO unico, sin correo electronico)
# ----------------------------------------------------------------
codigos = generar_codigos(CONFIG["num_estudiantes"])

estudiantes = []
for i in range(1, CONFIG["num_estudiantes"] + 1):
    nom = nombres[(i - 1) % len(nombres)]
    ape1 = apellidos[((i - 1) // len(nombres)) % len(apellidos)]
    ape2 = apellidos[(i * 3) % len(apellidos)]
    estudiantes.append({
        "id": i,
        "nombre": f"{nom} {ape1} {ape2}",
        "edad": random.randint(CONFIG["edad_min"], CONFIG["edad_max"]),
        "codigo": codigos[i - 1],
    })

# ----------------------------------------------------------------
# 2. Hobbies: los 40 fijos, ids 1..40
# ----------------------------------------------------------------
hobbies = [{"id": i + 1, "nombre": nombre}
           for i, nombre in enumerate(hobbies_nombres)]

# ----------------------------------------------------------------
# 3. Recompensas: las 40 fijas, la recompensa i es la del hobby i
# ----------------------------------------------------------------
recompensas = [{
    "id": i + 1,
    "nombre": nombre,
    "valor": random.randint(CONFIG["valor_min"], CONFIG["valor_max"]),
} for i, nombre in enumerate(recompensas_nombres)]

# ----------------------------------------------------------------
# 4. Hobbies de cada estudiante (solo para generar las realizaciones)
# ----------------------------------------------------------------
h_min, h_max = CONFIG["hobbies_por_estudiante"]
necesidades_h = [(e["id"], random.randint(h_min, h_max)) for e in estudiantes]
hobbies_de = repartir_sin_repetidos([h["id"] for h in hobbies], necesidades_h)

# ----------------------------------------------------------------
# 5. Realizacion_Hobby: varias por estudiante, total exacto.
#    La recompensa siempre corresponde al hobby de la realizacion.
# ----------------------------------------------------------------
r_min, r_max = CONFIG["realizaciones_por_estudiante"]
conteos = repartir_realizaciones(len(estudiantes),
                                 CONFIG["total_realizaciones"], r_min, r_max)
fecha_inicio = CONFIG["fecha_inicio"]
total_dias = (CONFIG["fecha_fin"] - fecha_inicio).days

filas = []
for e, cantidad in zip(estudiantes, conteos):
    for _ in range(cantidad):
        filas.append({
            "estudiante_id": e["id"],
            "fecha": (fecha_inicio + timedelta(days=random.randint(0, total_dias))).strftime("%Y-%m-%d"),
        })

# Se barajan para no agrupar por estudiante ni por fecha, y luego a cada
# realizacion se le asigna el hobby MENOS usado hasta ese momento (siempre
# dentro de los que practica ese estudiante), de modo que todos los
# hobbies quedan usados casi por igual.
random.shuffle(filas)
uso_hobby_temp = {h["id"]: 0 for h in hobbies}
for fila in filas:
    mis_hobbies = sorted(hobbies_de[fila["estudiante_id"]])
    h_id = min(mis_hobbies, key=lambda i: (uso_hobby_temp[i], random.random()))
    uso_hobby_temp[h_id] += 1
    fila["hobby_id"] = h_id
    fila["recompensa_id"] = h_id

realizaciones = [{"id": i, **f} for i, f in enumerate(filas, start=1)]

# ----------------------------------------------------------------
# Verificacion de integridad antes de escribir nada
# ----------------------------------------------------------------
assert len(hobbies) == len(recompensas), \
    "HOBBY y RECOMPENSA deben tener la misma cantidad (una por hobby)"
assert len({e["codigo"] for e in estudiantes}) == len(estudiantes), \
    "Codigos de estudiante duplicados"
assert all(len(e["codigo"]) == 11 for e in estudiantes), \
    "Codigo de estudiante fuera de estructura (debe tener 11 digitos)"
assert len(realizaciones) == CONFIG["total_realizaciones"], \
    "El total de realizaciones no coincide con CONFIG"
assert len({r["id"] for r in realizaciones}) == len(realizaciones), \
    "IDs duplicados en REALIZACION_HOBBY"
assert all(r["recompensa_id"] == r["hobby_id"] for r in realizaciones), \
    "Realizacion con recompensa distinta a la de su hobby"

# ----------------- ESCRIBIR CSVs -----------------

with open(os.path.join(CSV_DIR, "estudiante.csv"), "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "nombre", "edad", "codigo"])
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

with open(os.path.join(CSV_DIR, "realizacion_hobby.csv"), "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "estudiante_id", "hobby_id", "recompensa_id", "fecha"])
    writer.writeheader()
    writer.writerows(realizaciones)

# El archivo de la tabla que ya no existe no debe seguir en el repositorio
estudiante_hobby_csv = os.path.join(CSV_DIR, "estudiante_hobby.csv")
if os.path.exists(estudiante_hobby_csv):
    os.remove(estudiante_hobby_csv)

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
    f.write(f"--   REALIZACION_HOBBY: {len(realizaciones)} filas\n")
    f.write(f"-- Generado por generate_dataset.py (semilla={CONFIG['semilla']})\n")
    f.write("-- ============================================================\n\n")

    f.write("-- 1. Limpieza de tablas (incluye ESTUDIANTE_HOBBY de versiones anteriores)\n")
    f.write("DROP TABLE IF EXISTS REALIZACION_HOBBY, ESTUDIANTE_HOBBY, ESTUDIANTE, HOBBY, RECOMPENSA CASCADE;\n\n")

    f.write("CREATE TABLE ESTUDIANTE (\n")
    f.write("    ID INT PRIMARY KEY,\n")
    f.write("    NOMBRE VARCHAR(100),\n")
    f.write("    EDAD INT,\n")
    f.write("    CODIGO VARCHAR(11) UNIQUE\n")
    f.write(");\n\n")

    f.write("CREATE TABLE HOBBY (\n")
    f.write("    ID INT PRIMARY KEY,\n")
    f.write("    NOMBRE VARCHAR(100)\n")
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
    f.write("    FOREIGN KEY (ESTUDIANTE_ID) REFERENCES ESTUDIANTE(ID),\n")
    f.write("    FOREIGN KEY (HOBBY_ID) REFERENCES HOBBY(ID),\n")
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
        "ESTUDIANTE", ["ID", "NOMBRE", "EDAD", "CODIGO"], estudiantes,
        lambda e: f"({e['id']}, {escape_sql(e['nombre'])}, {e['edad']}, {escape_sql(e['codigo'])})",
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
        "REALIZACION_HOBBY", ["ID", "ESTUDIANTE_ID", "HOBBY_ID", "RECOMPENSA_ID", "FECHA"], realizaciones,
        lambda r: f"({r['id']}, {r['estudiante_id']}, {r['hobby_id']}, {r['recompensa_id']}, '{r['fecha']}')",
        f"-- 5. Insercion de {len(realizaciones)} REALIZACION_HOBBY\n")

print(f"SQL generado exitosamente en {SQL_FILE}")

# ----------------- RESUMEN DE DISTRIBUCION -----------------
real_por_alumno = Counter(r["estudiante_id"] for r in realizaciones)
uso_hobby = Counter(r["hobby_id"] for r in realizaciones)
uso_recompensa = Counter(r["recompensa_id"] for r in realizaciones)

print()
print("=" * 62)
print("RESUMEN DEL DATASET GENERADO")
print("=" * 62)
print(f"ESTUDIANTE        {len(estudiantes):>6} filas | "
      f"codigos unicos: {len(set(codigos))} | "
      f"ej: {estudiantes[0]['codigo']}, {estudiantes[1]['codigo']}")
print(f"HOBBY             {len(hobbies):>6} filas | "
      f"uso de cada hobby: {min(uso_hobby.values())}-{max(uso_hobby.values())}")
print(f"RECOMPENSA        {len(recompensas):>6} filas | "
      f"uso de cada recompensa: {min(uso_recompensa.values())}-{max(uso_recompensa.values())}")
print(f"REALIZACION       {len(realizaciones):>6} filas | "
      f"realizaciones/estudiante: {min(real_por_alumno.values())}-{max(real_por_alumno.values())}")
print("=" * 62)
