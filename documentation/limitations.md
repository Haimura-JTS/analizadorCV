# Limitaciones conocidas

## Lectura de PDF

- Solo se procesa texto extraible. Los documentos escaneados o compuestos
  unicamente por imagenes requieren OCR, que no forma parte de esta version.
- Los PDFs protegidos por contrasena se rechazan con un error controlado.
- El orden devuelto por PyMuPDF puede no coincidir con el orden visual en
  documentos con varias columnas, tablas o posicionamiento complejo.
- El limite de carga y procesamiento es de 10 MB.

## Deteccion y extraccion

- Los encabezados se reconocen por aliases exactos en espanol e ingles. Un
  titulo desconocido se conserva como contenido de la seccion activa, pero no
  abre una seccion nueva.
- Experiencia y formacion agrupan actualmente cada seccion completa en una
  unica entrada. No separan de forma fiable varios puestos o titulaciones.
- Nombre y titulo profesional solo se buscan en las primeras lineas y se
  descartan candidatos con apariencia de contacto o encabezado.
- Contacto se extrae mediante expresiones regulares y se conserva la primera
  coincidencia de cada tipo. Formatos atipicos pueden no detectarse.
- Las habilidades se separan por comas, punto y coma o barras verticales; no
  existe todavia una clasificacion semantica avanzada.
- Idiomas, certificaciones, cursos y proyectos usan reglas visibles y
  conservadoras. Los campos ambiguos permanecen como `None`.
- Las fechas admiten formatos comunes y precision parcial. Fechas ambiguas se
  convierten en `None` y generan una advertencia.

## Garantias y advertencias

- El analizador no completa informacion ausente ni consulta servicios
  externos.
- Las lineas anteriores al primer encabezado se conservan en
  `metadata.unclassified_text`.
- El contenido de secciones duplicadas se acumula y genera una advertencia.
- Un fallo de lectura produce el mismo contrato JSON, con
  `processed_successfully=false` y el motivo en `metadata.errors`.
- Los encabezados reconocidos no se duplican en la salida porque actuan como
  marcadores estructurales.

## Verificacion

La suite automatizada se ejecuto con Python 3.13.5. La inspeccion visual
interactiva de Streamlit sigue limitada al entorno local del usuario, aunque
sus estados principales se verifican mediante `streamlit.testing.v1.AppTest`.

Las ampliaciones propuestas se priorizan en
[`improvements.md`](improvements.md).
