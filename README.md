# Analizador de CV

Aplicacion academica para analizar curriculums en formato PDF y convertir la informacion extraida en una estructura JSON consistente.

## Objetivo

El proyecto se desarrollara por etapas. La primera version se centrara en:

- validar archivos PDF;
- extraer texto;
- limpiar contenido;
- detectar secciones principales;
- construir un JSON estructurado;
- conservar informacion no clasificada.

## Tecnologias previstas

- Python 3.11 o superior
- PyMuPDF para lectura de PDF
- Pydantic para validacion de modelos
- pytest para pruebas
- Streamlit para la interfaz web

## Estado actual

Etapa 9 implementada: la aplicacion dispone de pruebas unitarias, integracion
con PDFs sinteticos reales, casos invalidos y control de cobertura.

## Instalacion

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

## Pruebas

```powershell
python -m pytest
```

La suite mide cobertura de ramas del paquete `cv_analyzer` y exige un minimo
del 80%. La estrategia completa se documenta en
[`documentation/testing.md`](documentation/testing.md).

## Uso del pipeline

```python
from cv_analyzer.pipeline import process_cv_file

result = process_cv_file("curriculum.pdf")
```

La funcion devuelve siempre el contrato JSON del proyecto. Cuando el archivo
no puede procesarse, `metadata.processed_successfully` vale `false` y el motivo
queda registrado en `metadata.errors`.

## Interfaz

```powershell
streamlit run app.py
```

La interfaz permite seleccionar o arrastrar un PDF, iniciar el analisis,
consultar un resumen, revisar el texto extraido, inspeccionar el JSON y
descargar el resultado.

## Privacidad

- El analizador no consulta servicios externos.
- La copia creada en el sistema de archivos se elimina al terminar cada
  procesamiento.
- Streamlit mantiene el archivo seleccionado y el resultado en la sesion
  activa hasta que se reemplacen o finalice la sesion.

## Limitaciones actuales

- Las heuristicas de experiencia y formacion todavia agrupan cada seccion como
  un unico bloque.
- Los PDF escaneados sin capa de texto no se procesan mediante OCR.

El registro completo esta en
[`documentation/limitations.md`](documentation/limitations.md).
