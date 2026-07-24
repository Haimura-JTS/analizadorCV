# Arquitectura

## Enfoque

La aplicacion usara una arquitectura modular. La interfaz llamara a un pipeline y el pipeline coordinara modulos especializados.

## Flujo implementado

1. La interfaz entrega una ruta a `process_cv_file_with_details()`.
2. `pdf_reader` valida y extrae texto y metadatos.
3. `text_cleaner` normaliza el contenido.
4. `section_detector` agrupa las lineas.
5. Los extractores especializados interpretan cada bloque.
6. `json_builder` ensambla un resultado serializable.
7. `validators` normaliza fechas y valida el esquema con Pydantic.
8. El pipeline devuelve un JSON correcto o una salida de error con el mismo
   contrato.

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

En la Etapa 6 se anaden `date_normalizer.py`, `validators.py` y modelos
Pydantic en `cv_analyzer.models`. Estas piezas validan el contrato JSON y
generan advertencias sin cambiar la extraccion existente.

En la Etapa 7 se anade `pipeline.py` como unico coordinador del recorrido
completo. El modulo registra inicio, exito y fallos mediante `logging`, pero no
configura handlers: esa decision queda en la interfaz que lo consuma.

Los errores esperados de archivo se convierten en mensajes de
`metadata.errors`. Los fallos inesperados conservan su traza en el registro
tecnico y devuelven un mensaje generico. En ambos casos se valida la salida con
el mismo modelo Pydantic.

En la Etapa 8 se anade `app.py` como capa de presentacion Streamlit. La
interfaz solo gestiona carga, estado, vistas y descarga. Delega el
procesamiento en `process_cv_file_with_details()`, que mantiene la
compatibilidad de `process_cv_file()` y evita una segunda lectura para mostrar
el texto.

`ui_helpers.py` aisla la creacion y eliminacion de copias temporales, el nombre
de descarga, la serializacion JSON y el formato del tamano. La configuracion de
tema, privacidad del cliente y limite de carga vive en
`.streamlit/config.toml`.

## Flujo de interfaz

1. Streamlit recibe un unico PDF de hasta 10 MB.
2. La carga se escribe con un nombre saneado dentro de un directorio temporal.
3. El pipeline produce texto y resultado estructurado.
4. La copia temporal se elimina al salir del contexto, tambien ante errores.
5. La interfaz conserva texto y resultado en el estado de la sesion.
6. El usuario revisa las vistas y descarga el JSON serializado.
