# Planificacion

## Situacion final

El repositorio contiene la version de entrega `0.2.0`, que alcanza todas las
capas previstas: lectura, extraccion, validacion, pipeline, interfaz, pruebas y
documentacion.

Cada etapa fue revisada contra sus criterios de aceptacion antes de autorizar
la siguiente. Las limitaciones semanticas restantes estan documentadas y no
impiden la entrega del alcance obligatorio.

## Estado de las etapas

| Etapa | Base existente | Revision formal |
| --- | --- | --- |
| 0. Diagnostico inicial | Si | Completada |
| 1. Planificacion y entorno | Si | Completada |
| 2. Lectura y validacion del PDF | Si | Completada |
| 3. Limpieza y contacto | Si | Completada |
| 4. Deteccion de secciones | Si | Completada |
| 5. Extraccion estructurada | Parcial | Completada |
| 6. Fechas y validacion | Parcial | Completada |
| 7. Pipeline | Si | Completada |
| 8. Interfaz | Si | Completada |
| 9. Pruebas y robustez | Si | Completada |
| 10. Documentacion y entrega | Si | Completada |

## Etapa 1: planificacion y entorno

El alcance de esta etapa se limita a consolidar la base del proyecto:

- estructura `src` instalable y separada de la interfaz;
- Python 3.11 o superior;
- `pyproject.toml` como fuente principal de dependencias;
- `requirements.txt` como alternativa sencilla;
- entorno virtual local excluido de Git;
- README, esquema JSON, licencia y planificacion versionados;
- prueba basica de lectura real con PyMuPDF;
- decision de biblioteca PDF registrada en
  [`decisions/0001-pymupdf.md`](decisions/0001-pymupdf.md).

No se incorporan nuevas reglas de extraccion en esta etapa.

## Etapa 2: lectura y validacion del PDF

La revision del lector incorpora:

- mensajes publicos que no incluyen rutas locales;
- rechazo explicito de archivos de cero bytes y documentos sin paginas;
- deteccion diferenciada de PDF vacio, corrupto, protegido y posiblemente
  escaneado;
- advertencias para paginas vacias o con imagen sin texto dentro de un PDF que
  tambien contiene texto;
- excepciones nuevas compatibles con las clases publicas anteriores;
- conservacion de la causa original al convertir fallos de PyMuPDF;
- pruebas unitarias y recorridos completos del pipeline.

La deteccion de escaneo no incorpora OCR ni interpreta imagenes.

## Etapa 3: limpieza y contacto

La revision de datos basicos incorpora:

- eliminacion conservadora de caracteres invisibles y controles no utiles;
- normalizacion de espacios sin unir lineas diferentes;
- correo convencional y URLs con protocolo opcional;
- telefonos probables limitados a entre 9 y 15 digitos;
- rechazo de rangos de fechas y secuencias numericas demasiado cortas o largas;
- busqueda de nombre en las cinco primeras lineas;
- titulo profesional hasta tres lineas despues del nombre;
- descarte de encabezados, contactos, frases descriptivas y candidatos
  ambiguos;
- campos ausentes representados mediante `None`;
- JSON basico serializable sin modificar el contrato.

Las reglas completas y sus limites se describen en
[`heuristics.md`](heuristics.md).

## Etapa 4: deteccion de secciones

La revision del detector incorpora:

- aliases ampliados para las ocho secciones objetivo;
- normalizacion de mayusculas, acentos, espacios y decoracion exterior;
- encabezados con numeracion decimal o romana;
- variantes bilingues separadas por barra, tuberia o parentesis;
- rechazo de frases normales mediante coincidencia completa;
- acumulacion y advertencia de secciones duplicadas;
- conservacion en `unclassified` de combinaciones ambiguas;
- orden interno de encabezados disponible para pruebas y depuracion;
- conservacion de encabezados desconocidos dentro del bloque activo.

Al finalizar la etapa 4 no se interpretaba todavia la estructura interna de
experiencia, formacion, habilidades ni secciones adicionales.

## Etapa 5: extraccion estructurada

La revision de los extractores incorpora:

- utilidades comunes para vinetas, listas, fechas localizadas y comparaciones
  sin acentos;
- separacion ordenada de experiencias y estudios cuando existen encabezados
  estructurados o fechas que aportan un limite verificable;
- identificacion conservadora de empresa, puesto, institucion y titulacion;
- normalizacion inicial de fechas encontradas dentro de cada entrada;
- clasificacion de vinetas laborales entre responsabilidades y logros;
- habilidades agrupadas por etiquetas explicitas y vocabularios limitados;
- idiomas con nivel visible, certificaciones y cursos con campos separados;
- proyectos agrupados mediante etiquetas de nombre, descripcion, tecnologias
  y URL;
- advertencias indexadas para estructuras que no pueden resolverse con
  certeza;
- compatibilidad de las funciones publicas anteriores y conservacion del
  contrato JSON 1.0.

Las reglas no reconstruyen disposiciones visuales ni completan campos
ausentes. El texto de experiencia y formacion permanece en `description`.

## Etapa 6: fechas y validacion

La revision formal incorpora:

- formatos parciales `YYYY` y `YYYY-MM` sin completar dias inexistentes;
- meses textuales y numericos en espanol e ingles;
- rangos con guion, raya, `a`, `hasta`, `to` y `through`;
- aliases de actualidad aplicados a experiencia, formacion y cursos;
- comparacion de rangos mediante limites mensuales para respetar precisiones
  mixtas;
- conversion de fechas ambiguas a `None` con advertencias indexadas;
- modelos Pydantic estrictos para tipos, fechas, contacto y metadatos;
- `processed_at` obligatorio en UTC cuando esta presente;
- contadores de archivo y paginas no negativos;
- errores de validacion con la ruta del campo afectado;
- deduplicacion conservadora de listas escalares, sin eliminar entradas
  completas ni lineas no clasificadas;
- comprobaciones de fechas invertidas y actualidad incompatible con fecha
  final.

No se validan dias ni se deduce si un periodo sin fecha final sigue vigente.
La forma del contrato JSON permanece sin cambios.

## Etapa 7: pipeline

La revision formal del recorrido completo incorpora:

- API simple mediante `process_cv_file()` y variante detallada con texto;
- coordinacion secuencial de lector, limpieza, deteccion, extractores,
  constructor y validadores;
- traduccion diferenciada de errores de dominio, sistema operativo y fallos
  inesperados;
- mensajes de sistema de archivos que no exponen rutas locales;
- logging tecnico sin incluir el nombre del PDF en mensajes explicitos;
- conservacion del texto y metadatos ya obtenidos si falla una fase posterior;
- salida fallida validada con el mismo `CVResultModel`;
- saneamiento defensivo de contadores y advertencias en la ruta de error;
- copias de colecciones mutables en el constructor para evitar cambios
  laterales;
- pruebas de integracion para exito, errores esperados, fallos inesperados y
  resultados intermedios invalidos.

La biblioteca utiliza `logging` estandar y deja la configuracion de handlers
al programa consumidor. No se anade estado global ni una dependencia nueva.

## Etapa 8: interfaz

La revision formal de Streamlit incorpora:

- carga unica mediante seleccion o arrastre con limite visible de 10 MB;
- boton de analisis deshabilitado hasta disponer de un PDF;
- estado de procesamiento y salida controlada ante errores;
- descarga JSON situada junto a la cabecera del resultado;
- vistas separadas de resumen, texto extraido y JSON;
- metricas de archivo, paginas, elementos y advertencias;
- agrupacion y deduplicacion visual de mensajes;
- traduccion de estados internos para su lectura en tablas;
- foco visible y ajuste de textos largos;
- saneamiento de rutas, nombres reservados y nombres excesivamente largos;
- eliminacion de la copia temporal tanto en exito como en fallo;
- pruebas con `AppTest` y recorrido real responsive en Chrome.

La interfaz sigue siendo una capa de presentacion: no contiene heuristicas de
extraccion, validacion contractual ni persistencia de documentos.

## Etapa 9: pruebas y robustez

La revision formal de la matriz de pruebas incorpora:

- PDF textual sencillo con dos columnas posicionadas;
- comprobacion de que todas sus lineas llegan al texto extraido;
- conservacion de experiencia y formacion en sus descripciones;
- dos experiencias ordenadas con rangos historico y actual;
- CV sin experiencia, correo, telefono ni perfiles;
- CV con experiencia pero sin formacion;
- contacto precedido por iconos visuales;
- PDF valido renombrado con una extension no permitida;
- validacion de todos los recorridos mediante `CVResultModel`;
- documentacion explicita de casos cubiertos y limitaciones restantes.

Los nuevos casos no reprodujeron defectos en el codigo de produccion. Por ese
motivo no se modificaron extractores, validadores ni pipeline durante esta
etapa. La cobertura funcional se amplio sin cambiar heuristicas estables.

## Etapa 10: documentacion y entrega

La preparacion final incorpora:

- version de entrega 0.2.0 sincronizada entre paquete y `pyproject.toml`;
- changelog cerrado con fecha de publicacion;
- informe final independiente;
- enlaces entre documentos revisados automaticamente;
- instalacion comprobada en un entorno virtual nuevo;
- ejemplo, contrato JSON, suite y servidor verificados desde esa instalacion;
- revision de datos ficticios, rutas privadas y archivos ignorados;
- limpieza de caches, logs y resultados generados durante la comprobacion.

No se incorporan funciones nuevas en esta etapa. El contrato JSON mantiene su
version de procesamiento 1.0 y las ampliaciones siguen fuera del nucleo.

## Entregables existentes

- Paquete instalable desde `pyproject.toml`.
- Interfaz local en `app.py`.
- API `process_cv_file()`.
- Contrato Pydantic documentado.
- Pruebas unitarias e integracion.
- PDFs sinteticos y ejemplo reproducible.
- README, changelog, arquitectura, memoria y licencia.

## Verificacion

Para comprobar la base desde un entorno limpio:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m pip check
python -m pytest
python examples/run_example.py
python -m streamlit run app.py
```

La prueba `test_read_pdf_text_returns_text_and_metadata` crea un PDF textual
temporal con PyMuPDF, lo lee mediante el modulo del proyecto y comprueba texto,
paginas, tamano y advertencias.

## Evolucion

El plan incremental de las etapas 0 a 10 queda completado. Cualquier
ampliacion posterior debe partir de [`improvements.md`](improvements.md),
abrirse como un nuevo ciclo autorizado y mantener compatibilidad con el
contrato JSON 1.0.
