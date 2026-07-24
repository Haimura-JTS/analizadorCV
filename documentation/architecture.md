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

Existe el modulo inicial de lectura de PDF. Puede devolver solo texto mediante
`extract_text_from_pdf()` o texto con metadatos tecnicos mediante
`read_pdf_text()`.

En la Etapa 3 se anaden modulos independientes para preparar el texto,
extraer contacto, aplicar una heuristica inicial de nombre/titulo y construir
un JSON basico. Todavia no existe pipeline completo.

En la Etapa 4 se anade `section_detector.py`, responsable de agrupar lineas
limpias en secciones principales sin extraer aun objetos estructurados.

En la Etapa 5 se anaden extractores iniciales para experiencia, formacion,
habilidades y secciones adicionales. Estos extractores son conservadores:
preservan contenido y dejan campos ambiguos como `None`.
