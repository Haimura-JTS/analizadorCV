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
- Las lineas previas al primer encabezado se conservan en
  `metadata.unclassified_text`.
- Las advertencias no invalidan el resultado.
- Los errores establecen `processed_successfully` en `false`.

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

### Experience

`company`, `position`, `start_date`, `end_date`, `current`, `description`,
`responsibilities` y `achievements`.

### Languages

`language` y `level`.

### Certifications

`name`, `institution` y `date`.

### Courses

`name`, `institution`, `start_date`, `end_date` y `status`.

### Projects

`name`, `description`, `technologies` y `url`.

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
