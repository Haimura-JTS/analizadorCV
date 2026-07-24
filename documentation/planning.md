# Planificacion

## Alcance inicial

El proyecto se desarrollara por etapas para evitar introducir complejidad antes de estabilizar el nucleo.

## Etapa actual

Etapa 9 implementada: pruebas y robustez.

Se han incorporado PDFs sinteticos, recorridos reales de integracion, casos
invalidos, regresiones y un umbral de cobertura. La ejecucion permanece
pendiente hasta disponer de Python en `PATH`.

La siguiente etapa prevista es la Etapa 10: documentacion y entrega.

## Riesgos iniciales

- Python no esta disponible actualmente desde la terminal usada por Codex.
- Los PDF escaneados requeriran OCR en una ampliacion posterior.
- La precision de extraccion dependera del texto disponible en el PDF.
- Las heuristicas actuales conservan contenido, pero todavia no separan con
  precision multiples experiencias o titulaciones dentro de una misma seccion.
- La interfaz no ha podido ejecutarse visualmente en el entorno actual porque
  Python no esta disponible en PATH.
- El umbral de cobertura del 80% no se ha podido medir todavia por la misma
  limitacion del entorno.
