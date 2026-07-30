# Estrategia de pruebas

## Objetivo

Verificar los modulos de forma aislada y recorrer el pipeline completo con
PDFs reales generados durante las pruebas. Todos los datos usados son
ficticios.

## Ejecucion

La instalacion de desarrollo incluye `pytest` y `pytest-cov`.

```powershell
python -m pytest
```

Comandos utiles para aislar una capa:

```powershell
python -m pytest tests/unit
python -m pytest tests/integration
python -m pytest tests/integration/test_real_pdf_pipeline.py
```

La ejecucion general mide ramas y lineas de `cv_analyzer`, muestra las lineas
sin cubrir y exige un minimo del 80%. Las pruebas de Streamlit se ejecutan,
pero `app.py` no forma parte de ese umbral del nucleo.

## Cobertura funcional

La suite contiene 142 funciones de prueba, ademas de las variantes generadas
por casos parametrizados. Cubre:

- validacion de extension, existencia, tipo, cero bytes y tamano del archivo;
- PDFs textuales validos, sin paginas, vacios, corruptos y protegidos;
- documentos basados solo en imagenes y escaneos parciales;
- advertencias que identifican paginas vacias o sin texto extraible;
- lectura real de documentos de una y varias paginas;
- PDF sencillo de dos columnas con conservacion de lineas;
- varias experiencias y periodos historicos o actuales;
- ausencia explicita de experiencia, formacion y contacto;
- contactos precedidos por iconos visuales;
- PDF valido rechazado por utilizar una extension falsa;
- caracteres invisibles, controles, espacios no separables y entradas vacias;
- telefonos internacionales y rechazo de fechas o secuencias numericas;
- URLs con protocolo alternativo y puntuacion final;
- nombre tras encabezados, particulas, contactos intermedios y frases que no
  deben convertirse en titulo;
- limpieza de texto y conservacion de lineas no clasificadas;
- contacto, nombre y titulo con regresiones contra falsos positivos;
- encabezados principales y aliases ampliados en espanol e ingles;
- numeracion, decoracion y encabezados bilingues equivalentes;
- rechazo de frases normales y conservacion de combinaciones ambiguas;
- orden, acumulacion de secciones duplicadas y aliases sin colisiones;
- separacion de experiencias y estudios, orden de entradas y fechas
  localizadas;
- extraccion de empresa, puesto, institucion y titulacion sin completar datos;
- responsabilidades, logros y advertencias de ambiguedad;
- habilidades etiquetadas, clasificadas y deduplicadas;
- idiomas, certificaciones, cursos y proyectos estructurados;
- fechas numericas y textuales, rangos alternativos y actualidad;
- precision anual frente a mensual y deteccion de inversiones definitivas;
- fechas ambiguas convertidas en `None` con advertencias indexadas;
- modelos estrictos, metadatos UTC y errores con rutas de campo;
- deduplicacion controlada y conservacion de entradas completas;
- construccion y validacion estricta del contrato JSON;
- errores esperados e inesperados del pipeline;
- errores de sistema sin rutas expuestas y errores de dominio sin mensaje;
- fallos posteriores a la lectura con conservacion de texto y metadatos;
- resultados intermedios invalidos y saneamiento de la salida de emergencia;
- aislamiento de colecciones mutables recibidas por los constructores;
- helpers de archivos temporales, nombres extremos y serializacion;
- estados principales, metricas, mensajes agrupados y metadatos defensivos de
  la interfaz mediante `streamlit.testing.v1.AppTest`;
- validacion y ejecucion del ejemplo incluido en la documentacion.
- resolucion de enlaces Markdown relativos;
- sincronizacion de la version del paquete con `pyproject.toml`.

## Casos de integracion reales

`tests/fixtures/pdf_factory.py` construye los documentos dentro de `tmp_path`;
pytest los elimina al terminar. Los casos incluyen:

- CV completo en espanol distribuido en dos paginas;
- CV en ingles con aliases de seccion;
- CV con encabezados numerados, decorados y bilingues;
- CV sin encabezados, cuyas lineas deben quedar en `unclassified_text`;
- secciones duplicadas, cuyo contenido debe acumularse;
- CV sencillo de dos columnas;
- CV con dos experiencias y sin formacion;
- CV sin experiencia ni datos de contacto;
- PDF valido renombrado con extension `.txt`;
- PDF vacio, corrupto, cifrado y basado solo en imagenes;
- PDF con una pagina textual y otra posiblemente escaneada.

Todos los recorridos del pipeline, incluidos los fallidos, validan la salida
con `CVResultModel` y comprueban que pueda serializarse como JSON.

## Conservacion de informacion

La prueba del CV sin encabezados compara todas las lineas de entrada con
`metadata.unclassified_text`. La prueba de secciones duplicadas comprueba que
ambos bloques permanezcan en la descripcion y que se emita una advertencia.
La prueba de dos columnas comprueba todas las lineas del texto extraido y las
descripciones completas de experiencia y formacion.
Los encabezados reconocidos se usan como estructura y no se copian como datos.

## Matriz minima

| Caso | Evidencia principal | Estado |
| --- | --- | --- |
| Una columna | CV completo en espanol e ingles | Cubierto |
| Dos columnas | `test_two_column_pdf_preserves_text_and_structures_known_sections` | Cubierto |
| Espanol e ingles | PDFs integrales por idioma | Cubierto |
| Iconos | Contacto con prefijos visuales y encabezados decorados | Cubierto |
| Sin experiencia | CV disperso con formacion | Cubierto |
| Sin formacion | CV con varias experiencias | Cubierto |
| Sin telefono o correo | Contacto completamente ausente | Cubierto |
| Varias experiencias | Dos puestos ordenados y fechados | Cubierto |
| Fechas alternativas | Pruebas unitarias y recorridos integrales | Cubierto |
| Vacio, corrupto, protegido o escaneado | PDFs sinteticos especificos | Cubierto |
| Extension falsa o no PDF | Validacion unitaria e integracion real | Cubierto |
| Encabezados desconocidos | Texto no clasificado y encabezado ambiguo | Cubierto |
| Secciones duplicadas | Acumulacion y advertencia | Cubierto |

## Resultado verificado

La suite se ejecuto con Python 3.13.5 y las dependencias declaradas:

- 175 casos recopilados;
- 175 casos correctos;
- 0 fallos;
- 94,91% de cobertura total;
- umbral requerido del 80% superado.

El endpoint de salud de Streamlit respondio correctamente. Una comprobacion
local automatizada mediante Chrome y DevTools cargo un PDF sintetico, ejecuto
el pipeline y capturo los estados inicial y final a 1440 x 1100 y
390 x 844 pixeles. No se detecto desbordamiento horizontal. Los cinco
recorridos de interfaz mediante `AppTest` tambien pasaron.
