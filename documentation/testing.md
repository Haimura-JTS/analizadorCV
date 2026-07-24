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

La suite contiene 63 funciones de prueba, ademas de las variantes generadas
por casos parametrizados. Cubre:

- validacion de extension, existencia, tipo y tamano del archivo;
- PDFs textuales validos, vacios, corruptos y protegidos;
- lectura real de documentos de una y varias paginas;
- limpieza de texto y conservacion de lineas no clasificadas;
- contacto, nombre y titulo con regresiones contra falsos positivos;
- encabezados principales en espanol e ingles;
- acumulacion de secciones duplicadas con advertencia;
- extractores de experiencia, formacion, habilidades y secciones adicionales;
- normalizacion y coherencia basica de fechas;
- construccion y validacion estricta del contrato JSON;
- errores esperados e inesperados del pipeline;
- helpers de archivos temporales y serializacion;
- estados principales de la interfaz mediante `streamlit.testing.v1.AppTest`.

## Casos de integracion reales

`tests/fixtures/pdf_factory.py` construye los documentos dentro de `tmp_path`;
pytest los elimina al terminar. Los casos incluyen:

- CV completo en espanol distribuido en dos paginas;
- CV en ingles con aliases de seccion;
- CV sin encabezados, cuyas lineas deben quedar en `unclassified_text`;
- secciones duplicadas, cuyo contenido debe acumularse;
- PDF vacio, corrupto y cifrado.

Todos los recorridos del pipeline, incluidos los fallidos, validan la salida
con `CVResultModel` y comprueban que pueda serializarse como JSON.

## Conservacion de informacion

La prueba del CV sin encabezados compara todas las lineas de entrada con
`metadata.unclassified_text`. La prueba de secciones duplicadas comprueba que
ambos bloques permanezcan en la descripcion y que se emita una advertencia.
Los encabezados reconocidos se usan como estructura y no se copian como datos.

## Limitacion del entorno

Las pruebas estan implementadas, pero no se han podido ejecutar en esta
estacion porque Python no esta disponible en `PATH`. Tampoco se ha podido
iniciar Streamlit para la inspeccion visual. Por ello no se registra un
porcentaje de cobertura observado; el 80% es el umbral configurado que debera
confirmar la primera ejecucion con un entorno Python 3.11 o superior.
