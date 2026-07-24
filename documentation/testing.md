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
- Limpieza de espacios y lineas vacias.
- Extraccion de correo, telefono, LinkedIn, GitHub y portfolio.
- Estrategia inicial para nombre y titulo profesional.
- Construccion de JSON basico serializable.

## Limitacion actual

No se han podido ejecutar pruebas porque Python no esta disponible en PATH en el entorno actual.
