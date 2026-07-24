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

Etapa 1 en preparacion: estructura minima, dependencias y primera lectura de PDF.

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

## Limitaciones actuales

- No hay interfaz grafica todavia.
- No hay extraccion estructurada de datos personales.
- No hay deteccion de secciones implementada en esta etapa.
- Los PDF escaneados sin capa de texto no se procesan mediante OCR.

