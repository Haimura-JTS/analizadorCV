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

## Etapa 6

El esquema se valida con Pydantic. Las fechas normalizadas usan `YYYY-MM`
cuando hay mes y ano, `YYYY` cuando solo hay ano y `null` cuando el formato es
ambiguo. Las advertencias se registran en `metadata.warnings`.

## Etapa 7

El pipeline completa `source_file`, `file_size_bytes`, `page_count` y
`processed_at`. La marca temporal se expresa en ISO 8601 con zona UTC.

La salida mantiene el contrato aun cuando falle el procesamiento:

- `processed_successfully` pasa a `false`;
- `errors` contiene al menos un mensaje controlado;
- las secciones no disponibles conservan sus valores nulos o listas vacias;
- los metadatos conocidos antes del fallo se mantienen.
