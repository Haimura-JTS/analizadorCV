# Estrategia de pruebas

## Objetivo

Comprobar cada modulo de forma independiente antes de integrarlo en el pipeline.

## Pruebas iniciales

- Validacion de extension PDF.
- Error al recibir un archivo inexistente.
- Error cuando el PDF no contiene texto extraible.
- Extraccion de texto desde un PDF valido.
- Error al recibir una ruta que apunta a un directorio.
- Error al superar el tamano maximo configurado.
- Error controlado ante contenido PDF dañado o falso.
- Limpieza de espacios y lineas vacias.
- Extraccion de correo, telefono, LinkedIn, GitHub y portfolio.
- Estrategia inicial para nombre y titulo profesional.
- Construccion de JSON basico serializable.
- Normalizacion de encabezados con mayusculas, dos puntos y acentos.
- Deteccion de secciones principales en espanol e ingles.
- Conservacion de texto no clasificado.
- Acumulacion de secciones duplicadas con advertencias.
- Extraccion inicial de experiencia y formacion conservando descripciones.
- Separacion y deduplicacion de habilidades.
- Extraccion inicial de idiomas, certificaciones, cursos y proyectos.
- Normalizacion de fechas en formatos numericos y textuales.
- Deteccion de rangos actuales.
- Validacion del esquema JSON mediante Pydantic.
- Advertencias por campos ausentes e inconsistencias de fechas.

## Limitacion actual

No se han podido ejecutar pruebas porque Python no esta disponible en PATH en el entorno actual.
