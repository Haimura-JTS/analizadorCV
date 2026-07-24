# Esquema JSON

## Objetivo

El resultado final representara los datos extraidos del curriculum sin inventar informacion ausente.

## Regla general

- Usar `null` cuando no exista certeza suficiente.
- Usar listas vacias cuando un bloque repetible no tenga elementos.
- Conservar texto no clasificado en `metadata.unclassified_text`.

## Etapa 3

La funcion `build_basic_cv_result()` construye una primera version del esquema
con datos personales iniciales, contacto y listas vacias para bloques que aun
no se extraen.
