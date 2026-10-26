-- ============================================================
-- CONSULTAS BASICAS
-- Base de datos: distribuidas
-- ============================================================

-- 1. Ver todos los estudiantes.
SELECT *
FROM ESTUDIANTE
ORDER BY ID;

-- 2. Ver estudiantes mayores de 20 anos.
SELECT ID, NOMBRE, EDAD, CORREO_ELECTRONICO
FROM ESTUDIANTE
WHERE EDAD > 20
ORDER BY EDAD DESC;

-- 3. Buscar estudiantes cuyo nombre contenga 'a'.
SELECT ID, NOMBRE, EDAD
FROM ESTUDIANTE
WHERE NOMBRE ILIKE '%a%'
ORDER BY NOMBRE;

-- 4. Ver todos los hobbies.
SELECT *
FROM HOBBY
ORDER BY ID;

-- 5. Ver los hobbies de cada estudiante.
SELECT
	e.ID AS estudiante_id,
	e.NOMBRE AS estudiante,
	h.ID AS hobby_id,
	h.NOMBRE AS hobby
FROM ESTUDIANTE e
JOIN ESTUDIANTE_HOBBY eh ON eh.ESTUDIANTE_ID = e.ID
JOIN HOBBY h ON h.ID = eh.HOBBY_ID
ORDER BY e.ID, h.ID;

-- 6. Contar cuantos hobbies tiene cada estudiante.
SELECT
	e.ID AS estudiante_id,
	e.NOMBRE AS estudiante,
	COUNT(eh.HOBBY_ID) AS cantidad_hobbies
FROM ESTUDIANTE e
LEFT JOIN ESTUDIANTE_HOBBY eh ON eh.ESTUDIANTE_ID = e.ID
GROUP BY e.ID, e.NOMBRE
ORDER BY cantidad_hobbies DESC, e.ID;

-- 7. Ver cada realizacion con sus datos relacionados.
SELECT
	rh.ID AS realizacion_id,
	e.NOMBRE AS estudiante,
	h.NOMBRE AS hobby,
	r.NOMBRE AS recompensa,
	r.VALOR AS valor_unitario,
	rh.FECHA
FROM REALIZACION_HOBBY rh
JOIN ESTUDIANTE e ON e.ID = rh.ESTUDIANTE_ID
JOIN HOBBY h ON h.ID = rh.HOBBY_ID
JOIN RECOMPENSA r ON r.ID = rh.RECOMPENSA_ID
ORDER BY rh.FECHA, rh.ID;

-- ============================================================
-- CONSULTAS SOBRE EL TOTAL DE RECOMPENSAS
-- Total ganado = cantidad de realizaciones * valor unitario.
-- ============================================================

-- 8. Total general de recompensas entregadas.
SELECT
	COUNT(rh.ID) AS cantidad_realizaciones,
	COALESCE(SUM(r.VALOR), 0) AS total_recompensas
FROM REALIZACION_HOBBY rh
JOIN RECOMPENSA r ON r.ID = rh.RECOMPENSA_ID;

-- 9. Total de recompensas por estudiante, incluyendo estudiantes sin realizaciones.
SELECT
	e.ID AS estudiante_id,
	e.NOMBRE AS estudiante,
	COUNT(rh.ID) AS cantidad_realizaciones,
	COALESCE(SUM(r.VALOR), 0) AS total_recompensas
FROM ESTUDIANTE e
LEFT JOIN REALIZACION_HOBBY rh ON rh.ESTUDIANTE_ID = e.ID
LEFT JOIN RECOMPENSA r ON r.ID = rh.RECOMPENSA_ID
GROUP BY e.ID, e.NOMBRE
ORDER BY total_recompensas DESC, e.ID;

-- 10. Total de recompensas por hobby.
SELECT
	h.ID AS hobby_id,
	h.NOMBRE AS hobby,
	COUNT(rh.ID) AS cantidad_realizaciones,
	COALESCE(SUM(r.VALOR), 0) AS total_recompensas
FROM HOBBY h
LEFT JOIN REALIZACION_HOBBY rh ON rh.HOBBY_ID = h.ID
LEFT JOIN RECOMPENSA r ON r.ID = rh.RECOMPENSA_ID
GROUP BY h.ID, h.NOMBRE
ORDER BY total_recompensas DESC, h.ID;

-- 11. Total de recompensas por tipo de recompensa.
SELECT
	r.ID AS recompensa_id,
	r.NOMBRE AS recompensa,
	r.VALOR AS valor_unitario,
	COUNT(rh.ID) AS cantidad_entregas,
	COUNT(rh.ID) * r.VALOR AS total_recompensas
FROM RECOMPENSA r
LEFT JOIN REALIZACION_HOBBY rh ON rh.RECOMPENSA_ID = r.ID
GROUP BY r.ID, r.NOMBRE, r.VALOR
ORDER BY total_recompensas DESC, r.ID;

-- 12. Total de recompensas por fecha.
SELECT
	rh.FECHA,
	COUNT(rh.ID) AS cantidad_realizaciones,
	SUM(r.VALOR) AS total_recompensas
FROM REALIZACION_HOBBY rh
JOIN RECOMPENSA r ON r.ID = rh.RECOMPENSA_ID
GROUP BY rh.FECHA
ORDER BY rh.FECHA;

-- 13. Estudiante con mayor total de recompensas.
SELECT
	e.ID AS estudiante_id,
	e.NOMBRE AS estudiante,
	SUM(r.VALOR) AS total_recompensas
FROM ESTUDIANTE e
JOIN REALIZACION_HOBBY rh ON rh.ESTUDIANTE_ID = e.ID
JOIN RECOMPENSA r ON r.ID = rh.RECOMPENSA_ID
GROUP BY e.ID, e.NOMBRE
ORDER BY total_recompensas DESC
LIMIT 1;

-- 14. Promedio del valor de recompensa por realizacion.
SELECT
	ROUND(AVG(r.VALOR), 2) AS promedio_recompensa
FROM REALIZACION_HOBBY rh
JOIN RECOMPENSA r ON r.ID = rh.RECOMPENSA_ID;

-- 15. Total de recompensas dentro de un rango de fechas.
-- Cambia las fechas segun el periodo que quieras consultar.
SELECT
	COUNT(rh.ID) AS cantidad_realizaciones,
	COALESCE(SUM(r.VALOR), 0) AS total_recompensas
FROM REALIZACION_HOBBY rh
JOIN RECOMPENSA r ON r.ID = rh.RECOMPENSA_ID
WHERE rh.FECHA BETWEEN DATE '2026-09-01' AND DATE '2026-09-30';

-- 16. Estudiantes cuyo total de recompensas supera 50.
SELECT
	e.ID AS estudiante_id,
	e.NOMBRE AS estudiante,
	SUM(r.VALOR) AS total_recompensas
FROM ESTUDIANTE e
JOIN REALIZACION_HOBBY rh ON rh.ESTUDIANTE_ID = e.ID
JOIN RECOMPENSA r ON r.ID = rh.RECOMPENSA_ID
GROUP BY e.ID, e.NOMBRE
HAVING SUM(r.VALOR) > 50
ORDER BY total_recompensas DESC;
