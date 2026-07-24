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

## Etapa 4

El texto previo al primer encabezado se conserva como `unclassified`. Las
secciones detectadas podran alimentar los bloques `education`, `experience`,
`skills`, `languages`, `certifications`, `courses` y `projects` en etapas
posteriores.

## Etapa 5

Las secciones detectadas se convierten en objetos iniciales. Cuando no hay
certeza suficiente, los campos especificos quedan como `null` y el contenido
original se conserva en `description` o `name`.
