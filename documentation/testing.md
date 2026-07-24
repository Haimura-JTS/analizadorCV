# Estrategia de pruebas

## Objetivo

Comprobar cada modulo de forma independiente antes de integrarlo en el pipeline.

## Pruebas iniciales

- Validacion de extension PDF.
- Error al recibir un archivo inexistente.
- Error cuando el PDF no contiene texto extraible.
- Extraccion de texto desde un PDF valido.
- Error al recibir una ruta que apunta a un directorio.
- Error al superar el tamano maximo configurado.
- Error controlado ante contenido PDF dañado o falso.

## Limitacion actual

No se han podido ejecutar pruebas porque Python no esta disponible en PATH en el entorno actual.
