# Mejoras futuras

## Prioridad alta

### OCR

Detectar documentos sin capa de texto e integrar OCR local con advertencias
sobre calidad y coste de procesamiento.

### Separacion de entradas

Identificar varias experiencias y titulaciones dentro de una misma seccion.
La version actual conserva el bloque completo en una sola entrada.

### Orden de lectura

Reconstruir columnas, tablas y bloques posicionados para acercar el orden
extraido al orden visual.

### Integracion continua

Ejecutar la suite en Python 3.11 y versiones posteriores, publicar cobertura y
verificar la instalacion limpia en cada cambio.

## Prioridad media

- Ampliar aliases de encabezados sin introducir coincidencias parciales.
- Extraer empresa, puesto, institucion y titulacion con reglas verificables.
- Clasificar habilidades en lenguajes, herramientas, tecnicas y blandas.
- Detectar ubicacion sin confundirla con datos de contacto.
- Separar logros de responsabilidades.
- Mejorar fechas con rangos localizados y precisiones mixtas.
- Permitir varios correos, telefonos y perfiles cuando existan.

## Experiencia de usuario

- Mostrar una vista editable antes de descargar el JSON.
- Permitir corregir manualmente secciones no reconocidas.
- Comparar el texto original con los campos extraidos.
- Incorporar accesibilidad y pruebas visuales automatizadas.
- Ofrecer procesamiento por lotes con limites configurables.

## Calidad y operacion

- Anadir analisis estatico y formateo automatizado.
- Generar un esquema JSON formal desde los modelos Pydantic.
- Medir precision con un corpus anonimizado y versionado.
- Registrar metricas locales sin almacenar contenido personal.
- Incorporar empaquetado y publicaciones versionadas.

## Criterio para nuevas reglas

Cada mejora de extraccion debe:

1. Conservar el texto cuando no haya certeza.
2. Generar una advertencia ante ambiguedad relevante.
3. Mantener el contrato JSON.
4. Incluir pruebas unitarias e integracion.
5. Evitar datos personales reales en fixtures.
