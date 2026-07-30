# Mejoras futuras

## Prioridad alta

### OCR

Detectar documentos sin capa de texto e integrar OCR local con advertencias
sobre calidad y coste de procesamiento.

### Segmentacion avanzada de entradas

Usar posicion y tipografia del PDF para complementar los limites textuales
actuales y distinguir entradas sin fechas ni separadores.

### Orden de lectura

Reconstruir columnas, tablas y bloques posicionados para acercar el orden
extraido al orden visual.

### Integracion continua

Ejecutar la suite en Python 3.11 y versiones posteriores, publicar cobertura y
verificar la instalacion limpia en cada cambio.

## Prioridad media

- Ampliar aliases de encabezados sin introducir coincidencias parciales.
- Ampliar vocabularios de puestos, titulaciones, instituciones y habilidades
  con un corpus anonimizado y pruebas contra falsos positivos.
- Reconocer mas formatos multilinea de certificaciones, cursos y proyectos.
- Detectar ubicacion sin confundirla con datos de contacto.
- Refinar la separacion de logros y responsabilidades con reglas medibles.
- Incorporar dias, trimestres y formatos regionales adicionales sin completar
  precision ausente.
- Permitir varios correos, telefonos y perfiles cuando existan.

## Experiencia de usuario

- Mostrar una vista editable antes de descargar el JSON.
- Permitir corregir manualmente secciones no reconocidas.
- Comparar el texto original con los campos extraidos.
- Ampliar la accesibilidad con auditorias de tecnologias de apoyo y convertir
  la comprobacion visual responsive en una regresion versionada.
- Ofrecer procesamiento por lotes con limites configurables.

## Calidad y operacion

- Anadir analisis estatico y formateo automatizado.
- Incorporar identificadores de correlacion y logging estructurado sin datos
  del documento.
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
