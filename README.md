# Analizador de CV

Aplicacion local en Python que extrae texto de curriculums PDF, detecta sus
secciones principales y devuelve un resultado JSON consistente. Incluye una
interfaz Streamlit y una API de Python para integrar el pipeline en otros
programas. La version de entrega actual es la 0.2.0.

## Funcionalidades

- Validacion de archivos PDF de hasta 10 MB, incluidos archivos vacios,
  documentos sin paginas, contenido corrupto y proteccion por contrasena.
- Extraccion de texto y metadatos con PyMuPDF.
- Deteccion de PDF basado solo en imagenes y advertencias por paginas sin
  texto extraible.
- Limpieza conservadora de espacios, controles y caracteres invisibles.
- Extraccion de correo, telefono y enlaces con filtros contra falsos positivos.
- Deteccion de secciones en espanol e ingles con alias, numeracion,
  decoracion y encabezados bilingues equivalentes.
- Extraccion estructurada de experiencia y formacion con entradas ordenadas,
  campos identificables y conservacion del texto original del bloque.
- Clasificacion de habilidades, idiomas, certificaciones, cursos y proyectos
  mediante etiquetas, listas y separadores visibles.
- Advertencias indexadas cuando una estructura no permite decidir sin
  inventar informacion.
- Normalizacion de fechas parciales y periodos actuales en espanol e ingles.
- Validacion Pydantic estricta de fechas, contacto, metadatos y tipos.
- Advertencias de coherencia y deduplicacion controlada de listas escalares.
- Pipeline central con errores de sistema traducidos, logs sin nombres de
  archivo y salida contractual tambien ante fallos intermedios.
- Salida con el mismo contrato JSON ante exito o error.
- Interfaz para cargar, revisar y descargar el analisis.
- Procesamiento local sin consultas a servicios externos.

## Requisitos

- Python 3.11 o superior.
- Un PDF con capa de texto. Los documentos escaneados requieren OCR.

`pyproject.toml` es la fuente principal de dependencias. `requirements.txt`
se mantiene como alternativa de instalacion sencilla e incluye las
herramientas de prueba.

## Inicio rapido

```powershell
git clone https://github.com/Haimura-JTS/analizadorCV.git
cd analizadorCV
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m streamlit run app.py
```

Streamlit mostrara la URL local de la aplicacion en la terminal. Las
instrucciones para Windows, Linux y macOS se detallan en
[`documentation/installation.md`](documentation/installation.md).

## Uso

### Interfaz

1. Seleccionar o arrastrar un unico archivo PDF.
2. Pulsar **Analizar**.
3. Revisar las advertencias, metricas, resumen, texto extraido y JSON.
4. Descargar el resultado desde la cabecera del analisis.

La copia temporal del PDF se elimina al terminar el procesamiento, tambien
cuando ocurre un error.

### API de Python

```python
from cv_analyzer.pipeline import process_cv_file

result = process_cv_file("curriculum.pdf")

if result["metadata"]["processed_successfully"]:
    print(result["personal_data"])
else:
    print(result["metadata"]["errors"])
```

`process_cv_file()` siempre devuelve el contrato completo. La variante
`process_cv_file_with_details()` conserva ademas el texto extraido para
clientes que necesiten mostrarlo.

### Ejemplo reproducible

```powershell
python examples/run_example.py
```

El ejemplo usa datos ficticios, crea el PDF dentro de un directorio temporal
y escribe el JSON en `examples/output/sample_result.json`. El resultado de
referencia se encuentra en
[`examples/example_result.json`](examples/example_result.json).

## Pruebas

```powershell
python -m pytest
```

La configuracion mide cobertura de ramas del paquete `cv_analyzer`, muestra
lineas sin cubrir y exige un minimo del 80%. La verificacion final con Python
3.13.5 completo 175 casos y obtuvo una cobertura total del 94,91%. Los casos se
describen en
[`documentation/testing.md`](documentation/testing.md).

## Estructura

```text
.
|-- app.py
|-- examples/
|-- src/cv_analyzer/
|   |-- models/
|   |-- pdf_reader.py
|   |-- section_detector.py
|   |-- pipeline.py
|   `-- validators.py
|-- tests/
|   |-- fixtures/
|   |-- integration/
|   `-- unit/
`-- documentation/
```

La interfaz depende del pipeline; el pipeline coordina lectores, extractores,
constructores y validadores. Los detalles estan en
[`documentation/architecture.md`](documentation/architecture.md).

## Contrato JSON

Los datos ausentes usan `null`, las colecciones repetibles usan listas y los
diagnosticos se guardan en `metadata.warnings` y `metadata.errors`. El esquema
completo se documenta en
[`documentation/json_schema.md`](documentation/json_schema.md).

## Privacidad

- No se envian documentos ni datos a servicios externos.
- Los ejemplos no contienen datos personales reales.
- Los PDFs temporales de la interfaz y del ejemplo se eliminan tras su uso.
- Los resultados descargados quedan bajo control del usuario.

## Documentacion

- [Instalacion](documentation/installation.md)
- [Arquitectura](documentation/architecture.md)
- [Esquema JSON](documentation/json_schema.md)
- [Pruebas](documentation/testing.md)
- [Limitaciones](documentation/limitations.md)
- [Mejoras futuras](documentation/improvements.md)
- [Memoria tecnica](documentation/memoria.md)
- [Informe final](documentation/final_report.md)
- [Planificacion](documentation/planning.md)
- [Heuristicas](documentation/heuristics.md)
- [Decision sobre PyMuPDF](documentation/decisions/0001-pymupdf.md)
- [Changelog](CHANGELOG.md)

## Licencia

Distribuido bajo la licencia MIT. Consulte [LICENSE](LICENSE).
