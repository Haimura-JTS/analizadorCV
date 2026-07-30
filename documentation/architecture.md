# Arquitectura

## Vision general

La aplicacion usa una arquitectura modular con dependencias dirigidas hacia el
pipeline. La interfaz se limita a presentar datos y no contiene reglas de
extraccion.

```text
Streamlit / API de Python
          |
          v
       pipeline
          |
          +--> pdf_reader
          +--> text_cleaner
          +--> personal_extractor
          +--> contact_extractor
          +--> section_detector
          +--> extractores de seccion
          +--> json_builder
          `--> validators --> modelos Pydantic
```

## Componentes

| Componente | Responsabilidad |
| --- | --- |
| `app.py` | Carga, estado de sesion, vistas y descarga en Streamlit. |
| `ui_helpers.py` | Archivos temporales, nombres seguros y serializacion. |
| `pipeline.py` | Coordinacion del recorrido completo y manejo de errores. |
| `pdf_reader.py` | Validacion del archivo y extraccion de texto/metadatos. |
| `text_cleaner.py` | Caracteres invisibles, controles, espacios y lineas. |
| `section_detector.py` | Alias, normalizacion, orden y agrupacion de secciones. |
| `personal_extractor.py` | Nombre y titulo en las primeras lineas. |
| `contact_extractor.py` | Correo, telefono probable y enlaces normalizados. |
| `*_extractor.py` | Interpretacion conservadora de cada seccion. |
| `extraction_utils.py` | Vinetas, listas, fechas localizadas y comparaciones. |
| `date_normalizer.py` | Fechas parciales, rangos, actualidad y comparacion. |
| `json_builder.py` | Construccion del diccionario contractual. |
| `validators.py` | Fechas, duplicados, coherencia y errores indexados. |
| `models/cv_schema.py` | Tipos estrictos, restricciones y contrato Pydantic. |

## Flujo de datos

1. Streamlit recibe un `UploadedFile` o un cliente llama al pipeline con una
   ruta.
2. La interfaz escribe la carga en un directorio temporal mediante
   `temporary_uploaded_pdf()`.
3. `read_pdf_text()` valida ruta, extension, tamano y contenido no vacio.
4. PyMuPDF comprueba proteccion y numero de paginas antes de recorrerlas.
5. El lector extrae texto y detecta paginas vacias o posiblemente escaneadas.
6. El texto se limpia y divide en lineas no vacias.
7. Se detectan datos iniciales y se agrupan las lineas por seccion.
8. Cada extractor transforma su bloque sin completar campos ambiguos y
   devuelve advertencias cuando dispone de una variante detallada.
9. El pipeline filtra y agrega esas advertencias; `json_builder` ensambla
   copias de las colecciones recibidas.
10. `validators` normaliza fechas, deduplica listas seguras, revisa coherencia
    y valida con Pydantic.
11. El pipeline devuelve el JSON y, cuando se solicita, el texto extraido.
12. La interfaz elimina el archivo temporal al salir del contexto.

## Contratos

`process_cv_file()` devuelve siempre `dict[str, object]` compatible con
`CVResultModel`.

`process_cv_file_with_details()` devuelve `CVProcessingOutput`, compuesto por:

- `data`: el mismo diccionario contractual;
- `extracted_text`: texto disponible o `None` si la lectura fallo.

El texto completo no se duplica dentro del JSON. Se conservan en
`metadata.unclassified_text` las lineas anteriores al primer encabezado y los
bloques iniciados por una combinacion ambigua de secciones conocidas.

`SectionDetectionResult.section_order` registra internamente las secciones en
su orden de aparicion, incluidas repeticiones. Este dato facilita pruebas y
depuracion, pero no modifica el contrato JSON 1.0.

Los extractores mantienen funciones simples, como `extract_experience()`, para
los consumidores existentes. El pipeline utiliza las variantes
`*_with_warnings`, que devuelven entradas estructuradas y diagnosticos sin
alterar el esquema publico.

La deduplicacion se limita a habilidades, responsabilidades, logros,
tecnologias, advertencias y errores. Las listas de experiencias, estudios,
idiomas y texto no clasificado no se modifican porque una repeticion puede
representar informacion real.

## Manejo de errores

Los errores esperados heredan de `CVAnalyzerError` o son errores del sistema de
archivos. Se convierten en un resultado con:

- `metadata.processed_successfully = false`;
- al menos un mensaje en `metadata.errors`;
- metadatos tecnicos conocidos hasta el momento;
- secciones vacias con el mismo esquema.

Los errores de dominio conservan su mensaje publico. Los errores de sistema se
traducen por tipo para no exponer rutas: archivo ausente, directorio o acceso
fallido. Los fallos inesperados se registran con traza mediante `logging`; el
cliente recibe un mensaje generico.

Los mensajes explicitos del pipeline no incluyen el nombre del archivo. El
nombre se mantiene solo en `metadata.source_file`, donde forma parte del
contrato solicitado. Si el lector ya termino antes del fallo, se conservan
texto, numero de paginas y tamano validos.

La ruta de emergencia descarta contadores negativos y mensajes no textuales
antes de validar el resultado fallido. De esta forma un resultado intermedio
invalido no impide construir la respuesta contractual.

`ScannedPDFError` diferencia un documento basado solo en imagenes de un PDF
textual vacio. `PasswordProtectedPDFError` mantiene compatibilidad con
`ProtectedPDFError`, y `ScannedPDFError` con `EmptyDocumentError`.

## Estado y archivos temporales

El pipeline no mantiene estado global. Streamlit conserva el ultimo resultado
en `session_state`, mientras que cada PDF se guarda dentro de un
`TemporaryDirectory`. El contexto garantiza su eliminacion tanto en exito como
en excepciones.

La seleccion de un archivo nuevo elimina el resultado anterior. `app.py`
presenta el estado, los mensajes, las metricas y las vistas de resumen, texto y
JSON, pero delega todo el procesamiento en
`process_cv_file_with_details()`. Los mensajes vacios o repetidos se filtran
solo para su presentacion y no modifican el objeto contractual.

`ui_helpers.py` elimina componentes de ruta y caracteres no validos de los
nombres recibidos. Tambien limita el nombre temporal a 120 caracteres,
conserva la extension cuando es posible y protege nombres reservados de
Windows. Esta capa no interpreta el contenido del curriculum.

El ejemplo de `examples/run_example.py` aplica el mismo criterio: genera el PDF
en un directorio temporal y conserva unicamente el JSON de salida solicitado.

## Dependencias

- PyMuPDF: lectura y escritura de PDFs de prueba.
- Pydantic: contrato y validacion.
- Streamlit: interfaz web.
- pytest y pytest-cov: pruebas y cobertura de desarrollo.

No existe base de datos, servicio remoto ni dependencia de inteligencia
artificial externa.

## Principios aplicados

- Responsabilidad unica por modulo.
- Reglas de extraccion explicitas y conservadoras.
- Ausencia representada por `None`, nunca por datos inventados.
- Errores de lectura separados de advertencias de calidad.
- Contrato estable entre pipeline, interfaz y consumidores.
- Datos ficticios en pruebas y ejemplos.
