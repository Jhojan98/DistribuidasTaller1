# Guion: Implementación de una base de datos distribuida con CockroachDB

## 1. Introducción

Hola, en este video vamos a presentar el proceso que realizamos para implementar y probar una base de datos distribuida utilizando CockroachDB, Docker y nuestra base de datos de ejemplo llamada Hobbies.

El objetivo principal fue pasar de una arquitectura tradicional, donde toda la información se almacena en un único servidor, a una arquitectura distribuida, donde los datos se gestionan entre varios nodos que trabajan de manera coordinada.

Durante el proceso configuramos un clúster de tres nodos, migramos nuestra base de datos, generamos un conjunto de datos de prueba, ejecutamos consultas SQL y realizamos diferentes pruebas para comprobar el funcionamiento del sistema, especialmente su capacidad para continuar trabajando cuando uno de sus nodos deja de funcionar.

## 2. ¿Qué es una base de datos distribuida?

Primero, es importante entender qué es una base de datos distribuida.

En una base de datos tradicional, como PostgreSQL en nuestra implementación inicial, toda la información depende de un único servidor. Esto significa que, si ese servidor deja de funcionar, la base de datos también deja de estar disponible.

En cambio, una base de datos distribuida utiliza varios nodos que trabajan en conjunto para almacenar y gestionar la información.

Para nuestro proyecto utilizamos tres nodos: roach1, roach2 y roach3.

Estos nodos mantienen copias sincronizadas de los datos y se comunican entre sí para garantizar que la información se encuentre actualizada.

Esto nos proporciona dos ventajas importantes: la tolerancia a fallos y la posibilidad de escalar horizontalmente.

La tolerancia a fallos permite que el sistema continúe funcionando aunque uno de los nodos deje de estar disponible. Por otro lado, el escalamiento horizontal permite agregar nuevos nodos para distribuir mejor el trabajo, en lugar de depender únicamente de aumentar la capacidad de un solo servidor.

## 3. Migración de PostgreSQL a CockroachDB

Inicialmente, nuestra base de datos Hobbies estaba implementada utilizando PostgreSQL tradicional, dentro de la carpeta Hobbies.

Para realizar las pruebas de distribución, creamos una nueva configuración utilizando CockroachDB, dentro de la carpeta PruebasDistribuidas.

Elegimos CockroachDB porque es un motor de base de datos distribuida compatible con el protocolo y gran parte de la sintaxis de PostgreSQL.

Esto nos permitió reutilizar nuestros scripts SQL, incluyendo la creación de tablas, las relaciones entre ellas, las llaves foráneas y las consultas, sin tener que desarrollar nuevamente toda la base de datos.

La principal diferencia es que ahora trabajamos con tres nodos independientes, en lugar de un único servidor centralizado.

## 4. Configuración del clúster

Para configurar nuestro entorno utilizamos Docker y Docker Compose, lo que nos permitió levantar los tres nodos de manera organizada.

Desde la carpeta PruebasDistribuidas ejecutamos el comando:

`docker compose up -d`

Con esto iniciamos los tres contenedores de CockroachDB y un contenedor adicional encargado de inicializar el clúster.

Cada nodo tiene su propio puerto de conexión SQL: el nodo uno utiliza el puerto 26257, el nodo dos el 26258 y el nodo tres el 26259.

También configuramos sus respectivas consolas web de monitoreo.

Una vez iniciado el entorno, verificamos que los tres nodos estuvieran funcionando correctamente mediante un comando de estado de CockroachDB.

Un concepto importante de esta configuración es que no existe un nodo maestro y dos nodos secundarios. Los tres nodos tienen las mismas capacidades y podemos conectarnos a cualquiera de ellos para realizar operaciones.

Internamente, CockroachDB divide la información en bloques llamados rangos, que se distribuyen entre los nodos.

Además, cada rango se replica tres veces y utiliza el algoritmo Raft para coordinar las operaciones.

Por ejemplo, cuando realizamos una inserción, se necesita la confirmación de la mayoría de los nodos para considerar que la operación fue guardada correctamente. En nuestro clúster de tres nodos, esto significa que necesitamos al menos dos nodos disponibles.

## 5. Carga de la base de datos y generación del dataset

Después de configurar el clúster, procedimos a cargar nuestra base de datos Hobbies.

Para facilitar este proceso desarrollamos un script llamado cargar_datos.sh, que automatiza la creación de la base de datos, la creación de las tablas y la inserción de los registros.

También generamos un dataset más grande para realizar pruebas más completas.

Para esto utilizamos un programa en Python llamado generate_dataset.py, que permite crear información de manera automática y reproducible.

El conjunto de datos está compuesto por cinco tablas:

- ESTUDIANTE, con 500 registros.
- HOBBY, con 250 registros.
- RECOMPENSA, con 250 registros.
- ESTUDIANTE_HOBBY, con 2.042 registros.
- REALIZACION_HOBBY, con 1.951 registros.

En total, trabajamos con 4.993 registros distribuidos entre las cinco tablas.

Un aspecto importante fue mantener relaciones realistas entre los datos.

Por ejemplo, cada estudiante puede tener varios hobbies y varias realizaciones. Esto nos permitió representar correctamente las relaciones de muchos a muchos y realizar consultas más completas.

También implementamos mecanismos para distribuir los hobbies y las recompensas de manera equilibrada, evitando que algunos registros quedaran sin utilizar.

Para cargar toda esta información ejecutamos nuevamente el script cargar_datos.sh.

Utilizamos un archivo SQL generado automáticamente, en lugar de importar directamente los archivos CSV, para mantener el proceso compatible con nuestra versión gratuita de CockroachDB y evitar dependencias adicionales.

## 6. Ejecución de consultas y monitoreo

Una vez cargada la información, comenzamos a comprobar que la base de datos funcionara correctamente.

Para esto ejecutamos las consultas SQL que habíamos preparado previamente.

Realizamos consultas de selección, filtros, uniones entre tablas mediante JOIN y operaciones para obtener diferentes resultados relacionados con los estudiantes, sus hobbies y las recompensas.

Estas consultas nos permitieron comprobar que la estructura de la base de datos y sus relaciones seguían funcionando correctamente después de la migración.

También utilizamos herramientas visuales como DBeaver para conectarnos al clúster.

Gracias a la compatibilidad de CockroachDB con PostgreSQL, pudimos utilizar el mismo tipo de conexión, seleccionando PostgreSQL como controlador e indicando el puerto del nodo al que queríamos conectarnos.

Adicionalmente, aprovechamos la consola web de CockroachDB, disponible desde el navegador.

Esta consola nos permitió visualizar el estado de los tres nodos, consultar las bases de datos y las tablas, y observar diferentes métricas del sistema, como el uso de CPU y memoria, las operaciones de lectura y escritura y los tiempos de respuesta de las consultas.

## 7. Prueba de tolerancia a fallos

Una de las pruebas más importantes que realizamos fue comprobar qué sucede cuando uno de los nodos deja de funcionar.

Para ello, primero ejecutamos una consulta desde el nodo dos, solicitando los nombres de los estudiantes almacenados en la base de datos.

Después, simulamos una falla apagando el nodo uno mediante Docker.

Con el primer nodo apagado, volvimos a ejecutar exactamente la misma consulta, pero esta vez utilizando el nodo dos.

El resultado fue que la base de datos continuó respondiendo correctamente y devolvió la misma información.

Esto fue posible porque los nodos dos y tres todavía estaban disponibles y podían mantener el quórum necesario para continuar trabajando.

También verificamos el estado del clúster desde la consola web, donde se podía observar que el nodo uno aparecía como desconectado, mientras que el resto del sistema seguía operativo.

Finalmente, volvimos a encender el primer nodo y comprobamos que se reincorporaba al clúster y sincronizaba automáticamente la información pendiente.

Con este experimento demostramos una de las principales ventajas de una base de datos distribuida: puede continuar prestando servicio incluso cuando uno de sus nodos presenta una falla.

## 8. Modificación de la estructura de las tablas

Finalmente, también realizamos pruebas para comprobar cómo se pueden modificar las tablas dentro de una base de datos distribuida.

Por ejemplo, analizamos cómo agregar una nueva columna utilizando el comando ALTER TABLE.

Comprobamos que este procedimiento es prácticamente igual al que utilizaríamos en PostgreSQL.

La diferencia importante es que, aunque ejecutamos el cambio desde un solo nodo, CockroachDB se encarga de replicar la modificación del esquema entre los demás nodos mediante su mecanismo de consenso.

Por lo tanto, no necesitamos realizar el cambio manualmente en cada uno de ellos.

También revisamos que, cuando agregamos una columna obligatoria a una tabla que ya contiene información, debemos establecer un valor por defecto para los registros existentes.

Adicionalmente, analizamos cómo incorporar estos cambios directamente en el generador de datos, para que las nuevas columnas también se mantengan cuando volvamos a generar y cargar el dataset.

## 9. Conclusiones

En conclusión, mediante este proceso logramos implementar una base de datos distribuida utilizando CockroachDB, configurando un clúster de tres nodos y migrando nuestra base de datos Hobbies.

También conseguimos generar y cargar un conjunto de datos de prueba, ejecutar consultas SQL, monitorear el comportamiento del clúster y comprobar su tolerancia a fallos mediante la desconexión de uno de sus nodos.

Esta implementación nos permitió comprender de manera práctica conceptos fundamentales de las bases de datos distribuidas, como la replicación, el particionamiento, el consenso mediante Raft, el quórum y el escalamiento horizontal.

Finalmente, pudimos comprobar que una arquitectura distribuida ofrece ventajas importantes frente a una arquitectura centralizada, especialmente en términos de disponibilidad, distribución de la información y tolerancia a fallos.

Muchas gracias.