# Planificacion

## Version 0.1.0

Las diez etapas previstas estan implementadas:

1. Estructura inicial y alcance.
2. Lectura y validacion de PDF.
3. Limpieza, contacto y datos personales.
4. Deteccion de secciones.
5. Extraccion estructurada.
6. Fechas, modelos y validacion.
7. Pipeline completo.
8. Interfaz Streamlit.
9. Pruebas y robustez.
10. Documentacion y entrega.

## Entregables

- Paquete instalable desde `pyproject.toml`.
- Interfaz local en `app.py`.
- API `process_cv_file()`.
- Contrato Pydantic documentado.
- Pruebas unitarias e integracion.
- PDFs sinteticos y ejemplo reproducible.
- README, changelog, arquitectura, memoria y licencia.

## Verificacion

La instalacion editable y la suite se verificaron con Python 3.13.5 mediante
la ruta local del interprete. Para repetir la comprobacion:

```powershell
python -m pip install -e ".[dev]"
python -m pytest
python examples/run_example.py
python -m streamlit run app.py
```

## Evolucion

Las siguientes iteraciones deben partir de
[`improvements.md`](improvements.md) y mantener compatibilidad con el contrato
JSON 1.0.
