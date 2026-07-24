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
- Streamlit para una interfaz sencilla en una etapa posterior

## Estado actual

Etapa 7 completada: el pipeline conecta lectura, limpieza, deteccion de
secciones, extractores, normalizacion y validacion del resultado.

## Instalacion prevista

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Pruebas

```powershell
pytest
```

## Uso del pipeline

```python
from cv_analyzer.pipeline import process_cv_file

result = process_cv_file("curriculum.pdf")
```

La funcion devuelve siempre el contrato JSON del proyecto. Cuando el archivo
no puede procesarse, `metadata.processed_successfully` vale `false` y el motivo
queda registrado en `metadata.errors`.

## Limitaciones actuales

- No hay interfaz grafica todavia.
- Las heuristicas de experiencia y formacion todavia agrupan cada seccion como
  un unico bloque.
- Los PDF escaneados sin capa de texto no se procesan mediante OCR.
