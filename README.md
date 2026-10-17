# Evaluacion2

Proyecto de integración de APIs realizado en la VM DEVASC. Incluye la carga de libros en School Library y una aplicación de rutas con GraphHopper.

## Requisitos

- Python 3 y la biblioteca `requests`.
- Acceso a School Library desde la VM DEVASC.
- Una clave personal de GraphHopper para consultar rutas.

## Ejecución

Abre una terminal y entra a la carpeta del proyecto con `cd ~/Evaluacion2`.

Para consultar rutas, ejecuta `python3 rutas_graphhopper.py`. El programa solicita la clave de GraphHopper, el origen, el destino y el medio de transporte. Muestra la distancia, el tiempo y las indicaciones paso a paso en español. Escribe `s` o `salir` para terminar.

Para cargar y consultar libros, ejecuta `python3 cargar_50_libros.py`. El programa consulta todas las páginas del catálogo y completa hasta 50 libros generados. Solo solicita el token de School Library si faltan libros por crear.

Las claves y los tokens se ingresan durante la ejecución y no están guardados en los archivos del proyecto.