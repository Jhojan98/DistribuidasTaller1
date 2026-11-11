# Guion: Implementación y experimentación de una base de datos distribuida con CockroachDB

**Duración estimada: 8 a 9 minutos.**

## 1. Introducción (0:00 – 0:45)

Hola. En este video vamos a presentar el proceso que realizamos para implementar y evaluar una base de datos distribuida utilizando CockroachDB, Docker y nuestra base de datos de ejemplo llamada Hobbies.

El objetivo principal fue transformar una arquitectura tradicional, donde toda la información depende de un único servidor, en una arquitectura distribuida, donde varios nodos trabajan de manera coordinada.

Para comprobar su funcionamiento, configuramos un clúster de tres nodos y realizamos cuatro experimentos enfocados en la replicación de datos, los cambios en la estructura de las tablas, la tolerancia a fallos y el rendimiento.

A continuación, explicaremos cómo desarrollamos todo el proceso y qué resultados obtuvimos.

## 2. Conceptos y funcionamiento de una base de datos distribuida (0:45 – 1:40)

Primero, debemos entender la diferencia entre una base de datos centralizada y una distribuida.

En una base de datos tradicional, como PostgreSQL en nuestra implementación inicial, toda la información se encuentra en un único servidor. Por lo tanto, si ese servidor deja de funcionar, la base de datos también deja de estar disponible.

En cambio, una base de datos distribuida utiliza varios nodos que trabajan en conjunto para almacenar y gestionar la información.

En nuestro caso utilizamos CockroachDB, que permite distribuir los datos y mantener copias sincronizadas entre los diferentes nodos.

Para lograrlo, utiliza un mecanismo llamado Raft, que permite coordinar las operaciones mediante un sistema de consenso.

En nuestro clúster de tres nodos se necesita la confirmación de al menos dos para mantener el quórum y garantizar que las operaciones se realicen correctamente.

Esto permite tolerar la caída de un nodo, aunque no la caída de dos, porque en ese caso se pierde la mayoría necesaria.

## 3. Configuración del clúster y carga de datos (1:40 – 2:55)

Para implementar nuestra solución utilizamos Docker y Docker Compose.

Primero definimos los tres servicios correspondientes a los nodos roach1, roach2 y roach3, junto con un contenedor auxiliar encargado de inicializar el clúster.

También configuramos una red interna para permitir la comunicación entre los nodos y volúmenes independientes para conservar la información.

Una vez configurado todo, ejecutamos el comando Docker Compose para levantar los servicios y verificamos que los tres nodos aparecieran en estado activo.

Después procedimos a cargar nuestra base de datos Hobbies.

Para esto desarrollamos un generador en Python que permite crear datos de prueba de manera automática y reproducible.

Nuestro dataset está compuesto por cuatro tablas:

- ESTUDIANTE, con 500 registros.
- HOBBY, con 40 registros.
- RECOMPENSA, con 40 registros.
- REALIZACION_HOBBY, con 2.000 registros.

En total contamos con 2.580 registros.

También buscamos que los datos tuvieran relaciones realistas. Por ejemplo, cada estudiante puede tener varios hobbies y realizaciones, y las recompensas están relacionadas con los hobbies correspondientes.

Para cargar toda esta información utilizamos un script que crea la base de datos, genera las tablas e inserta los registros automáticamente.

## 4. Consultas SQL y herramientas de monitoreo (2:55 – 3:30)

Una vez cargada la información, comprobamos que la base de datos funcionara correctamente ejecutando diferentes consultas SQL.

Realizamos consultas de selección, filtros, agrupaciones y uniones entre tablas mediante JOIN.

Para facilitar las pruebas utilizamos DBeaver, donde configuramos tres conexiones independientes, una para cada nodo.

Esto nos permitió ejecutar operaciones desde un nodo y comprobar sus resultados desde los demás.

También utilizamos la consola web de CockroachDB, que nos permitió observar el estado de los nodos, las operaciones realizadas y diferentes métricas de rendimiento, como la latencia, el uso de recursos y las operaciones de lectura y escritura.

## 5. Experimento 1: Replicación de escrituras entre nodos (3:30 – 4:15)

El primer experimento tuvo como objetivo comprobar que los datos insertados desde un nodo fueran visibles desde los demás.

Para esto, primero insertamos un estudiante desde el nodo uno y posteriormente consultamos ese mismo registro desde el nodo dos.

Después repetimos el procedimiento, pero esta vez insertando información desde el nodo dos y consultándola desde el nodo tres.

En ambos casos pudimos observar que los registros estaban disponibles desde los otros nodos sin necesidad de realizar una inserción adicional.

Con esto comprobamos que los tres nodos trabajan sobre un mismo estado de datos y que las escrituras se replican correctamente.

## 6. Experimento 2: Modificación de la estructura de las tablas (4:15 – 5:00)

En el segundo experimento comprobamos cómo se comporta el clúster cuando necesitamos modificar la estructura de una tabla.

Para ello utilizamos el comando ALTER TABLE y agregamos una nueva columna llamada PAIS a la tabla ESTUDIANTE.

Lo importante de esta prueba es que ejecutamos el cambio únicamente desde el nodo uno.

Posteriormente revisamos la estructura de la tabla desde los nodos dos y tres y comprobamos que la nueva columna también estaba disponible.

Después asignamos diferentes países a los estudiantes y realizamos consultas para agrupar, filtrar y calcular las recompensas según el país.

Los resultados fueron consistentes al consultar desde los diferentes nodos.

Esto demuestra que los cambios en el esquema también se coordinan y replican automáticamente, sin necesidad de modificar cada nodo manualmente.

## 7. Experimento 3: Tolerancia a fallos (5:00 – 6:15)

El tercer experimento fue uno de los más importantes, porque nos permitió comprobar los límites de disponibilidad del clúster.

Realizamos dos pruebas.

En la primera apagamos uno de los tres nodos utilizando Docker.

Después intentamos consultar la información y realizar una nueva inserción desde los nodos que continuaban activos.

El resultado fue satisfactorio: el sistema siguió funcionando porque todavía teníamos dos nodos disponibles, suficientes para mantener el quórum.

En la segunda prueba apagamos también un segundo nodo, dejando solamente uno activo.

Esta vez, al intentar realizar consultas e inserciones, obtuvimos errores y tiempos de espera.

Esto ocurrió porque un solo nodo no es suficiente para alcanzar el quórum requerido por Raft.

Finalmente, volvimos a encender los nodos y comprobamos que el clúster se recuperó y que el registro insertado durante la primera prueba seguía disponible.

Con este experimento demostramos que CockroachDB puede tolerar la pérdida de un nodo en nuestra configuración de tres nodos, pero necesita mantener la mayoría para continuar operando.

## 8. Experimento 4: Comparación de rendimiento (6:15 – 7:25)

En el último experimento comparamos el rendimiento de una instancia de CockroachDB con un solo nodo frente a nuestro clúster completo de tres nodos.

Para realizar una comparación justa, preparamos dos entornos independientes con exactamente el mismo dataset.

Después ejecutamos la misma consulta compleja en ambos escenarios y medimos sus tiempos de respuesta utilizando EXPLAIN ANALYZE y las herramientas de monitoreo.

Los resultados fueron los siguientes:

En el escenario de un solo nodo obtuvimos un tiempo promedio de 8,5 milisegundos.

Mientras que en el clúster de tres nodos obtuvimos un promedio de 7,8 milisegundos.

Esto significa que, para la consulta evaluada, el clúster de tres nodos presentó un tiempo de respuesta ligeramente menor.

Aunque la diferencia no es muy grande, nos permite observar que la arquitectura distribuida también puede ofrecer resultados competitivos en rendimiento.

Sin embargo, es importante tener en cuenta que esta comparación corresponde a la consulta y al entorno que utilizamos, por lo que no significa que tres nodos siempre serán más rápidos que uno.

## 9. Conclusiones (7:25 – 8:30)

En conclusión, mediante este taller logramos implementar y evaluar una base de datos distribuida utilizando CockroachDB y un clúster de tres nodos.

Los experimentos nos permitieron comprobar que las escrituras realizadas desde un nodo están disponibles desde los demás y que los cambios en la estructura de las tablas se propagan automáticamente.

También comprobamos la importancia del quórum para garantizar la disponibilidad del sistema: con dos nodos activos la base de datos puede continuar funcionando, pero cuando solamente queda uno, pierde la capacidad de operar correctamente.

Por otra parte, la comparación de rendimiento mostró que, en nuestra prueba, el clúster de tres nodos obtuvo un tiempo de respuesta ligeramente menor que la instancia individual.

Finalmente, este trabajo nos permitió comprender de manera práctica conceptos fundamentales de las bases de datos distribuidas, como la replicación, el consenso mediante Raft, el quórum, la tolerancia a fallos y el escalamiento horizontal.

Más allá de la implementación, pudimos comprobar cómo estos mecanismos permiten construir sistemas que no dependen de un único servidor y que pueden mantener la disponibilidad de la información ante determinados fallos.

Muchas gracias.