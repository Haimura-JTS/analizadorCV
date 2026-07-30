# Esquema JSON

## Contrato

Cada llamada al pipeline devuelve las mismas claves de primer nivel:

| Campo | Tipo | Contenido |
| --- | --- | --- |
| `personal_data` | objeto | Nombre, titulo, ubicacion y resumen. |
| `contact` | objeto | Correo, telefono y URLs. |
| `education` | lista | Formacion academica detectada. |
| `experience` | lista | Experiencia profesional detectada. |
| `skills` | objeto | Habilidades agrupadas por categoria. |
| `languages` | lista | Idioma y nivel. |
| `certifications` | lista | Certificaciones. |
| `courses` | lista | Cursos. |
| `projects` | lista | Proyectos. |
| `metadata` | objeto | Trazabilidad, advertencias y errores. |

Los modelos fuente se encuentran en
`src/cv_analyzer/models/cv_schema.py`. Todos heredan de una configuracion que
rechaza campos inesperados.

## Reglas de representacion

- Un dato escalar ausente se representa con `null`.
- Un bloque repetible sin elementos se representa con `[]`.
- Una bandera siempre usa `true` o `false`.
- Una fecha usa `YYYY-MM`, `YYYY` o `null`.
- `processed_at` usa ISO 8601 con zona UTC.
- `file_size_bytes` y `page_count` son enteros no negativos o `null`.
- Correo y URLs de contacto deben cumplir sus formatos normalizados.
- Las lineas previas al primer encabezado se conservan en
  `metadata.unclassified_text`.
- Las entradas repetibles conservan el orden detectado dentro de su seccion.
- Los campos estructurales ambiguos permanecen en `null`; cuando es relevante,
  `metadata.warnings` identifica la seccion y el indice afectados.
- Las advertencias no invalidan el resultado.
- Los errores establecen `processed_successfully` en `false`.
- Un resultado no puede declarar exito si contiene errores.

Los modelos usan validacion estricta: no convierten cadenas como `"1"` en
enteros ni valores como `1` en booleanos. Los campos inesperados se rechazan.

## Estructura resumida

```json
{
  "personal_data": {
    "full_name": null,
    "professional_title": null,
    "location": null,
    "summary": null
  },
  "contact": {
    "email": null,
    "phone": null,
    "linkedin": null,
    "github": null,
    "portfolio": null
  },
  "education": [],
  "experience": [],
  "skills": {
    "technical": [],
    "tools": [],
    "programming_languages": [],
    "soft_skills": []
  },
  "languages": [],
  "certifications": [],
  "courses": [],
  "projects": [],
  "metadata": {
    "source_file": null,
    "file_size_bytes": null,
    "page_count": null,
    "processed_at": null,
    "processed_successfully": false,
    "processing_version": "1.0",
    "warnings": [],
    "errors": [],
    "unclassified_text": []
  }
}
```

## Entradas repetibles

### Education

`institution`, `degree`, `start_date`, `end_date`, `status` y `description`.
`status` puede ser `in_progress` cuando el rango indica actualidad.
`description` conserva el bloque textual completo de la entrada.

### Experience

`company`, `position`, `start_date`, `end_date`, `current`, `description`,
`responsibilities` y `achievements`.

Las responsabilidades y los logros conservan el orden de sus vinetas. La
descripcion mantiene todas las lineas usadas para construir la entrada.

### Languages

`language` y `level`.

### Certifications

`name`, `institution` y `date`.

### Courses

`name`, `institution`, `start_date`, `end_date` y `status`.
`status` puede ser `in_progress`.

### Projects

`name`, `description`, `technologies` y `url`.

## Normalizacion y coherencia

Los meses y anos reconocibles se convierten antes de validar el esquema. Un
valor ambiguo se sustituye por `null` y produce una advertencia con la ruta,
por ejemplo `experience[0].start_date`.

Una fecha anual representa un intervalo de enero a diciembre al comprobar
orden. Por ello, `2024-12` seguido de `2024` no se considera definitivamente
invertido, mientras que `2025-01` seguido de `2024` si genera una advertencia.

Los duplicados se eliminan sin distinguir mayusculas solo dentro de listas
escalares seguras. Se conserva el primer valor y se registra una advertencia.
No se eliminan entradas completas ni lineas de `unclassified_text`.

## Resultado fallido

Un error de archivo no cambia la forma del documento. Las secciones permanecen
vacias y `metadata` contiene:

```json
{
  "processed_successfully": false,
  "warnings": [],
  "errors": [
    "El PDF no contiene texto extraible."
  ]
}
```

Las demas claves de `metadata` siguen presentes. El ejemplo completo de una
salida correcta esta en
[`../examples/example_result.json`](../examples/example_result.json).

Un PDF basado solo en imagenes utiliza el mismo contrato y comunica que parece
escaneado en `metadata.errors`. Si solo algunas paginas carecen de texto, el
procesamiento puede completarse y sus numeros se conservan en
`metadata.warnings`.

Los errores de sistema operativo se traducen antes de entrar en el JSON. Las
rutas locales y el detalle de excepciones inesperadas no se incluyen en
`metadata.errors`. Si un fallo ocurre despues de leer el PDF, los metadatos
tecnicos validos ya disponibles se mantienen en la salida fallida.
