# Arquitectura

## Enfoque

La aplicacion usara una arquitectura modular. La interfaz llamara a un pipeline y el pipeline coordinara modulos especializados.

## Flujo previsto

1. Carga de archivo.
2. Validacion y lectura del PDF.
3. Limpieza del texto.
4. Deteccion de secciones.
5. Extraccion de informacion.
6. Validacion.
7. Construccion del JSON.
8. Visualizacion y descarga desde la interfaz.

## Estado actual

Solo existe el modulo inicial de lectura de PDF.

