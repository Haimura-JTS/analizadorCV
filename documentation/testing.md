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
- Integracion completa desde la lectura simulada del PDF hasta el JSON final.
- Salida valida ante errores esperados de archivo.
- Mensaje publico controlado y registro tecnico ante fallos inesperados.
- Sustitucion de resultados intermedios invalidos por una salida contractual.
- Respuesta detallada del pipeline con texto y JSON en una unica lectura.
- Creacion y eliminacion de archivos temporales de interfaz.
- Saneamiento de nombres de archivo para rutas y caracteres no validos.
- Serializacion JSON Unicode y construccion del nombre de descarga.
- Formato visual de tamanos de archivo.
- Arranque simulado de la interfaz y presencia del flujo de carga mediante
  `streamlit.testing.v1.AppTest`.

## Limitacion actual

Las pruebas estan implementadas, pero no se han podido ejecutar porque Python
no esta disponible en PATH en el entorno actual. Por el mismo motivo tampoco se
ha podido iniciar Streamlit para realizar una inspeccion visual en navegador.
