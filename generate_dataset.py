#!/usr/bin/env python3
import csv
import os
import random
from datetime import date, timedelta

random.seed(42)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_DIR = os.path.join(BASE_DIR, "datos_csv")
SQL_FILE = os.path.join(BASE_DIR, "cargar_500_datos.sql")

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

# 1. Generar 500 Estudiantes
estudiantes = []
for i in range(1, 501):
    nom = nombres[(i - 1) % len(nombres)]
    ape1 = apellidos[((i - 1) // len(nombres)) % len(apellidos)]
    ape2 = apellidos[(i * 3) % len(apellidos)]
    nombre_completo = f"{nom} {ape1} {ape2}"
    edad = 18 + ((i * 7) % 15)  # Edades entre 18 y 32
    # correo normalizado sin tildes ni espacios
    clean_nom = nom.lower().replace(" ", "")
    clean_ape = ape1.lower().replace(" ", "")
    correo = f"{clean_nom}.{clean_ape}{i}@universidad.edu.co"
    estudiantes.append({
        "id": i,
        "nombre": nombre_completo,
        "edad": edad,
        "correo_electronico": correo
    })

# 2. Generar 500 Hobbies
actividades = [
    "Futbol", "Baloncesto", "Voleibol", "Natacion", "Ajedrez", "Ciclismo", "Senderismo",
    "Atletismo", "Tenis de campo", "Tenis de mesa", "Pintura al oleo", "Acuarela",
    "Dibujo digital", "Escultura", "Fotografia urbana", "Fotografia de naturaleza",
    "Guitarra acustica", "Guitarra electrica", "Piano", "Bateria", "Bajo electrico",
    "Canto coral", "Produccion musical", "Lectura de ciencia ficcion", "Lectura de historia",
    "Escritura creativa", "Poesia", "Programacion en Python", "Desarrollo web",
    "Robótica educativa", "Modelado 3D", "Animacion digital", "Videojuegos de estrategia",
    "Videojuegos de rol", "Juegos de mesa", "Cocina italiana", "Reposteria artesanal",
    "Cocteleria sin alcohol", "Barismo y cafe", "Jardineria urbana", "Bonsai", "Yoga",
    "Meditacion guiada", "Calistenia", "Crossfit", "Artes marciales", "Teatro callejero",
    "Danza contemporanea", "Salsa y bachata", "Origami y papiroflexia"
]

niveles_ambientes = [
    "Nivel Principiante", "Nivel Intermedio", "Nivel Avanzado", "En Grupo", "Al Aire Libre",
    "En Laboratorio", "Taller Intensivo", "Modalidad Nocturna", "De Fin de Semana", "Club Competitivo"
]

hobbies = []
h_id = 1
for act in actividades:
    for mod in niveles_ambientes:
        hobbies.append({
            "id": h_id,
            "nombre": f"{act} ({mod})"
        })
        h_id += 1
        if h_id > 500:
            break
    if h_id > 500:
        break

# 3. Generar 500 Recompensas
tipos_recompensa = [
    "Bono Cafeteria", "Descuento Libreria", "Puntos Bienestar", "Insignia Deportiva",
    "Acceso Gimnasio", "Bono Almuerzo", "Kit Papeleria", "Entrada Cine Cultural",
    "Certificado Excelencia", "Bono Tienda Universitaria"
]

recompensas = []
for i in range(1, 501):
    tipo = tipos_recompensa[(i - 1) % len(tipos_recompensa)]
    nivel = ((i - 1) // len(tipos_recompensa)) + 1
    nombre_rec = f"{tipo} - Nivel {nivel}"
    valor = 10 + ((i * 13) % 491)  # Valores entre 10 y 500
    recompensas.append({
        "id": i,
        "nombre": nombre_rec,
        "valor": valor
    })

# 4. Generar 500 Estudiante_Hobby
# Cada estudiante del 1 al 500 con un hobby asignado (todos los pares son unicos)
estudiante_hobbies = []
for i in range(1, 501):
    # Asignar a estudiante i un hobby h
    # Hobby variado
    h_idx = ((i * 17) % 500) + 1
    estudiante_hobbies.append({
        "estudiante_id": i,
        "hobby_id": h_idx
    })

# 5. Generar 500 Realizaciones de Hobbies
# Cada realizacion usa un par valido de (estudiante_id, hobby_id)
# Fecha entre 2026-01-01 y 2026-10-15
fecha_inicio = date(2026, 1, 1)
total_dias = (date(2026, 10, 15) - fecha_inicio).days

realizaciones = []
for i in range(1, 501):
    par = estudiante_hobbies[i - 1]
    recompensa_id = ((i * 23) % 500) + 1
    offset_dias = (i * 7) % total_dias
    fecha_realizacion = fecha_inicio + timedelta(days=offset_dias)
    realizaciones.append({
        "id": i,
        "estudiante_id": par["estudiante_id"],
        "hobby_id": par["hobby_id"],
        "recompensa_id": recompensa_id,
        "fecha": fecha_realizacion.strftime("%Y-%m-%d")
    })

# ----------------- ESCRIBIR CSVs -----------------

# Estudiante CSV
with open(os.path.join(CSV_DIR, "estudiante.csv"), "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "nombre", "edad", "correo_electronico"])
    writer.writeheader()
    writer.writerows(estudiantes)

# Hobby CSV
with open(os.path.join(CSV_DIR, "hobby.csv"), "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "nombre"])
    writer.writeheader()
    writer.writerows(hobbies)

# Recompensa CSV
with open(os.path.join(CSV_DIR, "recompensa.csv"), "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "nombre", "valor"])
    writer.writeheader()
    writer.writerows(recompensas)

# Estudiante_Hobby CSV
with open(os.path.join(CSV_DIR, "estudiante_hobby.csv"), "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["estudiante_id", "hobby_id"])
    writer.writeheader()
    writer.writerows(estudiante_hobbies)

# Realizacion_Hobby CSV
with open(os.path.join(CSV_DIR, "realizacion_hobby.csv"), "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "estudiante_id", "hobby_id", "recompensa_id", "fecha"])
    writer.writeheader()
    writer.writerows(realizaciones)

print(f"CSVs creados exitosamente en {CSV_DIR}")

# ----------------- ESCRIBIR SQL -----------------

def escape_sql(val):
    if isinstance(val, str):
        return "'" + val.replace("'", "''") + "'"
    elif isinstance(val, date):
        return f"'{val.strftime('%Y-%m-%d')}'"
    return str(val)

with open(SQL_FILE, "w", encoding="utf-8") as f:
    f.write("-- ============================================================\n")
    f.write("-- CARGA DE 500 DATOS POR TABLA PARA EL CLUSTER COCKROACHDB\n")
    f.write("-- Base de datos: hobbies\n")
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

    # Inserciones en bloques de 100 para ESTUDIANTE
    f.write("-- 2. Insercion de 500 ESTUDIANTES\n")
    chunk_size = 100
    for c in range(0, len(estudiantes), chunk_size):
        chunk = estudiantes[c:c+chunk_size]
        vals = ",\n".join(
            f"({e['id']}, {escape_sql(e['nombre'])}, {e['edad']}, {escape_sql(e['correo_electronico'])})"
            for e in chunk
        )
        f.write(f"INSERT INTO ESTUDIANTE (ID, NOMBRE, EDAD, CORREO_ELECTRONICO) VALUES\n{vals};\n\n")

    # Inserciones en bloques de 100 para HOBBY
    f.write("-- 3. Insercion de 500 HOBBIES\n")
    for c in range(0, len(hobbies), chunk_size):
        chunk = hobbies[c:c+chunk_size]
        vals = ",\n".join(
            f"({h['id']}, {escape_sql(h['nombre'])})"
            for h in chunk
        )
        f.write(f"INSERT INTO HOBBY (ID, NOMBRE) VALUES\n{vals};\n\n")

    # Inserciones en bloques de 100 para RECOMPENSA
    f.write("-- 4. Insercion de 500 RECOMPENSAS\n")
    for c in range(0, len(recompensas), chunk_size):
        chunk = recompensas[c:c+chunk_size]
        vals = ",\n".join(
            f"({r['id']}, {escape_sql(r['nombre'])}, {r['valor']})"
            for r in chunk
        )
        f.write(f"INSERT INTO RECOMPENSA (ID, NOMBRE, VALOR) VALUES\n{vals};\n\n")

    # Inserciones en bloques de 100 para ESTUDIANTE_HOBBY
    f.write("-- 5. Insercion de 500 ESTUDIANTE_HOBBY\n")
    for c in range(0, len(estudiante_hobbies), chunk_size):
        chunk = estudiante_hobbies[c:c+chunk_size]
        vals = ",\n".join(
            f"({eh['estudiante_id']}, {eh['hobby_id']})"
            for eh in chunk
        )
        f.write(f"INSERT INTO ESTUDIANTE_HOBBY (ESTUDIANTE_ID, HOBBY_ID) VALUES\n{vals};\n\n")

    # Inserciones en bloques de 100 para REALIZACION_HOBBY
    f.write("-- 6. Insercion de 500 REALIZACION_HOBBY\n")
    for c in range(0, len(realizaciones), chunk_size):
        chunk = realizaciones[c:c+chunk_size]
        vals = ",\n".join(
            f"({rh['id']}, {rh['estudiante_id']}, {rh['hobby_id']}, {rh['recompensa_id']}, '{rh['fecha']}')"
            for rh in chunk
        )
        f.write(f"INSERT INTO REALIZACION_HOBBY (ID, ESTUDIANTE_ID, HOBBY_ID, RECOMPENSA_ID, FECHA) VALUES\n{vals};\n\n")

print(f"SQL generado exitosamente en {SQL_FILE}")
