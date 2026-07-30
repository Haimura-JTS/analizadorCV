# Changelog

Este archivo registra los cambios relevantes del proyecto.

## Unreleased

No hay cambios pendientes documentados.

## 0.2.0 - 2026-07-30

### Added

- Deteccion especifica de PDFs compuestos solo por imagenes.
- Advertencias con numero de pagina para escaneos parciales y paginas vacias.
- Validacion explicita de archivos de cero bytes y documentos sin paginas.
- Excepciones compatibles para PDF escaneado y proteccion por contrasena.
- Pruebas unitarias e integracion para los nuevos casos de lectura.
- Limpieza de caracteres invisibles, guiones blandos y controles no utiles.
- Validacion de candidatos de telefono mediante longitud de 9 a 15 digitos.
- Busqueda conservadora de nombre y titulo dentro del encabezado inicial.
- Pruebas de regresion para fechas, URLs, encabezados y frases descriptivas.
- Alias adicionales para las ocho secciones principales en espanol e ingles.
- Encabezados numerados, decorados y bilingues equivalentes.
- Registro interno del orden de aparicion de secciones, incluidas duplicadas.
- Advertencias para encabezados que combinan secciones incompatibles.
- Prueba integral con encabezados decorados y bilingues.
- Separacion ordenada de experiencias y estudios mediante encabezados y
  fechas visibles.
- Extraccion conservadora de empresa, puesto, institucion, titulacion y fechas.
- Clasificacion de vinetas de experiencia entre responsabilidades y logros.
- Habilidades agrupadas por etiquetas y vocabularios verificables.
- Idiomas, certificaciones, cursos y proyectos con formatos estructurados.
- Resultados de extraccion con advertencias indexadas para datos ambiguos.
- Pruebas unitarias e integracion para entradas multiples y campos parciales.
- Rangos de fecha con separadores alternativos y comparacion sin falsos
  positivos por precision anual o mensual.
- Deteccion de actualidad para experiencia, formacion y cursos.
- Tipado Pydantic estricto para fechas, contacto y metadatos tecnicos.
- Validacion UTC de `processed_at` y limites no negativos para metadatos.
- Deduplicacion controlada de habilidades, vinetas, tecnologias y mensajes.
- Errores de esquema que incluyen la ruta exacta del campo afectado.
- Traduccion de errores del sistema de archivos sin exponer rutas locales.
- Conservacion del texto y metadatos ya leidos ante fallos posteriores.
- Saneamiento de metadatos internos en la salida de emergencia.
- Copias defensivas de habilidades, advertencias y texto no clasificado.
- Pruebas de integracion para errores esperados, inesperados y de contrato.
- Descarga JSON accesible desde la cabecera del resultado.
- Foco visible para acciones y ajuste de texto en anchos reducidos.
- Pruebas de interfaz para metricas, avisos agrupados y metadatos anomalos.
- Limite defensivo para nombres temporales excesivamente largos.
- PDF sintetico de dos columnas con comprobacion de conservacion de contenido.
- Recorridos integrales para varias experiencias y secciones ausentes.
- Regresion para contactos precedidos por iconos visuales.
- Caso de PDF valido rechazado por utilizar una extension falsa.

### Changed

- Los errores de ruta inexistente o directorio ya no incluyen rutas locales.
- Las URLs conservan protocolos existentes y eliminan puntuacion de la frase.
- Los datos de contacto intermedios pueden omitirse al buscar el titulo.
- Los encabezados ambiguos y su contenido se conservan en `unclassified`.
- El pipeline agrega las advertencias de todos los extractores sin alterar el
  contrato JSON.
- Las fechas ambiguas se convierten en `null` con una advertencia indexada.
- Los errores previos fuerzan `processed_successfully=false` antes de validar.
- Los mensajes de log del pipeline ya no incluyen el nombre del PDF.
- Las advertencias vacias, repetidas o de tipo incorrecto se filtran en el
  limite de orquestacion.
- La interfaz agrupa errores y advertencias repetidos en alertas compactas.
- Los estados internos `in_progress` se muestran como `En curso`.
- Los tamanos o contadores booleanos se presentan como datos no disponibles.

### Documentation

- Alineada la planificacion con la revision incremental por etapas.
- Registrada la decision tecnica de utilizar PyMuPDF.
- Corregida la etiqueta del boton de analisis descrita en el README.
- Documentadas las heuristicas de limpieza, contacto, nombre y titulo.
- Documentadas las reglas y limitaciones de deteccion de secciones.
- Documentadas las heuristicas y limitaciones de extraccion estructurada.
- Documentadas las reglas de fechas, coherencia y deduplicacion.
- Documentados el flujo completo, los limites de error y la privacidad del log.
- Documentada la interfaz, su validacion responsive y sus limites operativos.
- Documentada la matriz de robustez y la trazabilidad de casos minimos.

## 0.1.0 - 2026-07-24

### Added

- Estructura modular del paquete `cv_analyzer`.
- Validacion de extension, ruta, tamano, cifrado y contenido extraible.
- Lectura de texto y metadatos PDF mediante PyMuPDF.
- Limpieza de texto y deteccion de secciones en espanol e ingles.
- Extractores de datos personales, contacto, experiencia, formacion,
  habilidades, idiomas, certificaciones, cursos y proyectos.
- Normalizacion inicial de fechas y advertencias de consistencia.
- Modelos Pydantic y contrato JSON estable para resultados correctos y fallidos.
- Pipeline central con registro tecnico y manejo controlado de errores.
- Interfaz Streamlit con carga, estado, vistas y descarga JSON.
- Helpers para archivos temporales, nombres seguros y serializacion.
- Pruebas unitarias, integracion simulada y recorridos con PDFs sinteticos.
- Casos para documentos vacios, corruptos, cifrados, sin encabezados y con
  secciones duplicadas.
- Cobertura de ramas configurada con un umbral minimo del 80%.
- Ejemplo ejecutable y resultado JSON de referencia con datos ficticios.
- Documentacion de instalacion, arquitectura, esquema, pruebas, limitaciones,
  mejoras y memoria tecnica.
- Licencia MIT.

### Fixed

- Deteccion de PDFs protegidos y errores de lectura.
- Conservacion del contenido de secciones duplicadas con advertencia.
- Falsos positivos que trataban datos de contacto como titulo profesional.
- Falsos positivos que trataban fragmentos de correo como URLs de portfolio.
- Reconocimiento del encabezado ingles simple `EXPERIENCE`.
