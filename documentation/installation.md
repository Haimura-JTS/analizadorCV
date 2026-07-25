# Instalacion

## Requisitos previos

- Git.
- Python 3.11 o superior disponible desde la terminal.
- Acceso a internet durante la instalacion de dependencias.

Compruebe Python antes de continuar:

```powershell
python --version
```

## Obtener el proyecto

```powershell
git clone https://github.com/Haimura-JTS/analizadorCV.git
cd analizadorCV
```

## Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Si PowerShell bloquea la activacion, puede ejecutar directamente:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m streamlit run app.py
```

## Linux y macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Instalacion minima

Para usar la aplicacion sin herramientas de prueba:

```powershell
python -m pip install -e .
```

`requirements.txt` ofrece una alternativa que incluye tambien las
dependencias de desarrollo:

```powershell
python -m pip install -r requirements.txt
```

## Ejecutar la interfaz

Desde la raiz:

```powershell
python -m streamlit run app.py
```

La terminal mostrara la URL local. Para detener el servidor, use `Ctrl+C`.

## Ejecutar el ejemplo

```powershell
python examples/run_example.py
```

El JSON generado se guarda en `examples/output/sample_result.json`.

## Ejecutar pruebas

```powershell
python -m pytest
```

Para separar capas:

```powershell
python -m pytest tests/unit
python -m pytest tests/integration
```

## Verificacion de la instalacion

Una instalacion preparada debe cumplir:

1. `python -c "import cv_analyzer"` termina sin error.
2. `python -m streamlit run app.py` inicia el servidor.
3. `python examples/run_example.py` genera un JSON correcto.
4. `python -m pytest` ejecuta la suite y comprueba el umbral de cobertura.

## Configuracion

La version 0.1.0 no requiere variables de entorno ni credenciales.

- El limite de archivo se define en `src/cv_analyzer/config.py`.
- El tema y opciones de Streamlit viven en `.streamlit/config.toml`.
- `.streamlit/secrets.toml` esta ignorado y no debe versionarse.

## Problemas frecuentes

### Python no se reconoce

Instale Python 3.11 o superior y habilite su incorporacion a `PATH`, o use la
ruta completa del ejecutable.

### El PDF no contiene texto extraible

El archivo puede ser un escaneo. Esta version no incorpora OCR.

### El PDF esta protegido

Guarde una copia sin contrasena antes de procesarlo.

### La cobertura queda por debajo del umbral

Revise las lineas mostradas por `pytest-cov` y anada casos que recorran el
comportamiento faltante.
