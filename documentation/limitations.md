# Limitaciones conocidas

## Lectura de PDF

- Solo se procesa texto extraible. Un documento compuesto unicamente por
  imagenes se identifica como posible escaneo y se rechaza con un error
  controlado. Si combina paginas textuales y paginas con imagen sin texto, el
  procesamiento continua con una advertencia que identifica esas paginas.
- La deteccion de escaneo es conservadora: se basa en ausencia de texto y
  presencia de imagenes. No evalua la calidad visual ni aplica OCR.
- Los PDFs protegidos por contrasena se rechazan con un error controlado.
- El orden devuelto por PyMuPDF puede no coincidir con el orden visual en
  documentos con varias columnas, tablas o posicionamiento complejo.
- La suite incluye un PDF sintetico sencillo de dos columnas y comprueba que
  conserve sus lineas y secciones. Esto no garantiza el orden correcto para
  todas las combinaciones de columnas, cajas flotantes o texto superpuesto.
- El limite de carga y procesamiento es de 10 MB.

## Deteccion y extraccion

- Los encabezados se reconocen por aliases explicitos en espanol e ingles tras
  normalizar acentos, numeracion y decoracion. No se usan coincidencias
  parciales.
- Un encabezado bilingue se acepta solo cuando todas sus partes corresponden a
  la misma seccion. Una combinacion de secciones diferentes se conserva en
  `unclassified` y genera una advertencia.
- Un titulo completamente desconocido se conserva como contenido de la seccion
  activa, pero no abre una seccion nueva. Sin tipografia no puede distinguirse
  con seguridad de una empresa, titulacion o descripcion breve.
- Se conserva el orden dentro de cada bloque y el orden interno de encabezados,
  pero el JSON agrupado no representa el intercalado global de secciones.
- Experiencia y formacion separan entradas solo cuando hay encabezados, cargos
  o fechas visibles. Bloques sin esas pistas pueden permanecer unidos, y un
  layout complejo puede producir limites imperfectos. El bloque interpretado
  se conserva siempre en `description`.
- Empresa, puesto, institucion y titulacion dependen de vocabularios
  deliberadamente acotados. Los campos no demostrables quedan en `None` y
  generan una advertencia indexada.
- Solo las vinetas con verbos de resultado o medidas conocidas se clasifican
  como logros. Una redaccion diferente puede permanecer como responsabilidad.
- Nombre se busca solo en las cinco primeras lineas. La regla admite entre dos
  y cinco palabras latinas con capitalizacion de nombre, permite particulas
  frecuentes y descarta encabezados, contactos y terminos profesionales
  conocidos. Nombres en otros alfabetos o escritos completamente en minusculas
  pueden no detectarse.
- El titulo se busca hasta tres lineas despues del nombre. Se rechazan frases
  con mas de ocho palabras, terminacion de oracion, apariencia de nombre,
  encabezado o contacto. Un cargo atipico puede permanecer en `None`.
- Contacto conserva la primera coincidencia de cada tipo. Un telefono probable
  debe contener entre 9 y 15 digitos; un identificador numerico con esa longitud
  todavia podria producir un falso positivo.
- Las URLs deben contener un dominio reconocible. Se anade `https://` cuando
  falta protocolo y se retira puntuacion final frecuente.
- Las habilidades se separan por comas, punto y coma o barras verticales. Las
  etiquetas explicitas tienen prioridad; el vocabulario automatico es limitado
  y los valores desconocidos se conservan en `technical`.
- Idiomas aceptan niveles visibles, pero no los traducen ni ordenan por
  competencia. Un nivel desconocido se conserva con una advertencia.
- Certificaciones y cursos solo separan institucion y fecha con estructuras
  visibles, principalmente barras verticales. Los formatos libres permanecen
  como nombre.
- Los proyectos se agrupan con etiquetas conocidas. Sin ellas, cada linea se
  conserva como un proyecto independiente y no se reconstruyen descripciones
  multilinea por tipografia.
- Las fechas admiten meses textuales o numericos y anos aislados. No se
  interpretan dias, estaciones, trimestres ni expresiones aproximadas.
- Una comparacion con precisiones mixtas solo avisa cuando la inversion es
  definitiva. No se inventa un mes para resolver el orden.
- La actualidad se reconoce mediante aliases completos. La ausencia de fecha
  final no basta para deducir que un periodo sigue vigente.
- La deduplicacion solo afecta listas escalares conocidas. Experiencias,
  estudios, idiomas y texto no clasificado pueden conservar repeticiones.

## Garantias y advertencias

- El analizador no completa informacion ausente ni consulta servicios
  externos.
- Las lineas anteriores al primer encabezado se conservan en
  `metadata.unclassified_text`.
- El contenido de secciones duplicadas se acumula y genera una advertencia.
- Un fallo de lectura produce el mismo contrato JSON, con
  `processed_successfully=false` y el motivo en `metadata.errors`.
- Los errores de acceso del sistema se comunican de forma generica para evitar
  exponer rutas; el detalle original no forma parte del JSON.
- Los encabezados reconocidos no se duplican en la salida porque actuan como
  marcadores estructurales.

`metadata.source_file` conserva el nombre del PDF porque forma parte del
contrato. Los mensajes explicitos del pipeline no lo escriben en el log. Las
trazas de fallos inesperados son tecnicas y no deben publicarse ni incorporarse
al repositorio.

## Verificacion

La suite automatizada se ejecuto con Python 3.13.5 y completo 175 casos. Los
estados principales se
verifican mediante `streamlit.testing.v1.AppTest`. Ademas, se recorrio la carga
y el procesamiento de un PDF sintetico en Chrome local a 1440 x 1100 y
390 x 844 pixeles. No se detecto desbordamiento horizontal; esta comprobacion
visual no sustituye pruebas en todos los navegadores ni tecnologias de apoyo.

Las ampliaciones propuestas se priorizan en
[`improvements.md`](improvements.md).
