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
| `text_cleaner.py` | Normalizacion de espacios y lineas. |
| `section_detector.py` | Agrupacion por encabezados conocidos. |
| `personal_extractor.py` | Heuristica inicial de nombre y titulo. |
| `contact_extractor.py` | Correo, telefono y enlaces. |
| `*_extractor.py` | Interpretacion conservadora de cada seccion. |
| `date_normalizer.py` | Fechas individuales y rangos. |
| `json_builder.py` | Construccion del diccionario contractual. |
| `validators.py` | Normalizacion final, advertencias y validacion. |
| `models/cv_schema.py` | Tipos Pydantic y prohibicion de campos inesperados. |

## Flujo de datos

1. Streamlit recibe un `UploadedFile` o un cliente llama al pipeline con una
   ruta.
2. La interfaz escribe la carga en un directorio temporal mediante
   `temporary_uploaded_pdf()`.
3. `read_pdf_text()` valida extension, existencia, tamano y proteccion.
4. PyMuPDF extrae el texto de todas las paginas y metadatos tecnicos.
5. El texto se limpia y divide en lineas no vacias.
6. Se detectan datos iniciales y se agrupan las lineas por seccion.
7. Cada extractor transforma su bloque sin completar campos ambiguos.
8. `json_builder` ensambla todas las piezas.
9. `validators` normaliza fechas, genera advertencias y valida con Pydantic.
10. El pipeline devuelve el JSON y, cuando se solicita, el texto extraido.
11. La interfaz elimina el archivo temporal al salir del contexto.

## Contratos

`process_cv_file()` devuelve siempre `dict[str, object]` compatible con
`CVResultModel`.

`process_cv_file_with_details()` devuelve `CVProcessingOutput`, compuesto por:

- `data`: el mismo diccionario contractual;
- `extracted_text`: texto disponible o `None` si la lectura fallo.

El texto completo no se duplica dentro del JSON. Solo se conservan en
`metadata.unclassified_text` las lineas anteriores al primer encabezado.

## Manejo de errores

Los errores esperados heredan de `CVAnalyzerError` o son errores del sistema de
archivos. Se convierten en un resultado con:

- `metadata.processed_successfully = false`;
- al menos un mensaje en `metadata.errors`;
- metadatos tecnicos conocidos hasta el momento;
- secciones vacias con el mismo esquema.

Los fallos inesperados se registran con traza mediante `logging`. El cliente
recibe un mensaje generico para no exponer detalles internos.

## Estado y archivos temporales

El pipeline no mantiene estado global. Streamlit conserva el ultimo resultado
en `session_state`, mientras que cada PDF se guarda dentro de un
`TemporaryDirectory`. El contexto garantiza su eliminacion tanto en exito como
en excepciones.

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
