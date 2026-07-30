# Heuristicas de extraccion

## Principio general

Las reglas priorizan evitar datos inventados. Cuando un valor no cumple las
condiciones minimas, el extractor devuelve `None` o una lista vacia. Las
heuristicas no consultan servicios externos ni intentan confirmar identidades.

## Limpieza de texto

Suposicion:

El texto extraido puede contener espacios repetidos, tabuladores, guiones
blandos, marcas de ancho cero, BOM y controles sin significado visible.

Reglas:

- se eliminan guiones blandos, marcas de ancho cero, BOM y controles no utiles;
- espacios, tabuladores y espacios no separables se reducen a un solo espacio;
- los saltos de linea se conservan durante la normalizacion;
- las lineas vacias se eliminan del texto preparado para extraccion.

Limitaciones:

No se reconstruyen columnas ni palabras divididas entre lineas. El texto
original permanece disponible en `CVProcessingOutput.extracted_text`; el texto
normalizado se utiliza internamente.

## Correo

Se reconoce una direccion convencional con usuario, `@`, dominio y extension
alfabetica de al menos dos caracteres. No se implementa RFC 5322 completo y se
conserva solo la primera coincidencia.

## Telefono

El patron localiza secuencias con digitos, espacios, parentesis, puntos o
guiones. Despues se cuentan los digitos:

- menos de 9: se descarta;
- entre 9 y 15: se acepta como candidato;
- mas de 15: se descarta.

Esto evita interpretar rangos como `2020 - 2024` como telefono. Un identificador
numerico de longitud telefonica todavia puede ser un falso positivo. El formato
visual detectado se conserva, salvo la reduccion de espacios repetidos.

## Enlaces

Se reconocen dominios con protocolo opcional y ruta opcional. Si falta
protocolo se anade `https://`. La puntuacion frecuente al final de una frase se
retira. Los dominios incluidos dentro de un correo se excluyen.

LinkedIn y GitHub se identifican por su dominio. La primera URL restante se
considera portfolio, por lo que un enlace externo no personal puede quedar
clasificado de ese modo.

## Nombre

Se inspeccionan como maximo las cinco primeras lineas. Un candidato debe:

- contener entre dos y cinco palabras;
- usar letras latinas y separadores simples;
- presentar capitalizacion compatible con un nombre;
- no ser un encabezado, un dato de contacto o un termino profesional conocido.

Se permiten particulas frecuentes como `de`, `del`, `la`, `van` o `von`.
Encabezados como `Curriculum Vitae`, `CV` o `Resume` se descartan.

La regla puede omitir nombres en otros alfabetos, escritos completamente en
minusculas o con formatos no previstos. Ante esa ambiguedad devuelve `None`.

## Titulo profesional

Una vez encontrado el nombre, se inspeccionan hasta tres lineas posteriores.
Los contactos intermedios se omiten y la busqueda termina al encontrar el
encabezado de una seccion. Un candidato se descarta si:

- supera 120 caracteres u ocho palabras;
- termina como una oracion con punto, exclamacion o interrogacion;
- parece otro nombre, un encabezado o un dato de contacto.

La regla evita usar frases de resumen como cargo, pero puede omitir titulos
largos o atipicos. No se genera ningun valor cuando no hay certeza suficiente.

## Encabezados de seccion

Se reconocen perfil, experiencia, formacion, habilidades, idiomas,
certificaciones, cursos y proyectos mediante aliases explicitos en espanol e
ingles.

Antes de comparar se aplican estas transformaciones:

- conversion a minusculas y eliminacion de acentos;
- reduccion de espacios;
- retirada de decoracion exterior como guiones, puntos o vinetas;
- retirada de numeracion como `1.`, `2 -` o `IV)`;
- conversion de `&` a `and` para aliases registrados.

Un encabezado bilingue separado por `/`, `|` o parentesis se acepta solo si
todas sus partes son aliases conocidos de la misma seccion. Por ejemplo,
`Experiencia / Work Experience` se clasifica como experiencia.

Si las partes apuntan a secciones diferentes, la linea y su contenido posterior
se conservan en `unclassified` hasta el siguiente encabezado valido y se genera
una advertencia. No se elige una seccion de forma arbitraria.

Los encabezados desconocidos no pueden distinguirse con seguridad de una
empresa, titulacion u otra linea corta porque el pipeline textual no conserva
tipografia. Por ese motivo se mantienen dentro de la seccion activa. Las frases
normales nunca se aceptan mediante coincidencias parciales.

El detector conserva el orden de las lineas dentro de cada bloque y registra el
orden de aparicion de encabezados conocidos. El JSON sigue agrupando los datos
por seccion, por lo que no representa el intercalado global completo.

## Experiencia

Las lineas no vacias se agrupan en entradas cuando aparece un nuevo encabezado
estructurado o cuando una fecha posterior aporta un limite verificable. Se
admiten encabezados con separadores visibles como `Empresa - Puesto`,
`Puesto | Empresa` o `Puesto @ Empresa`.

Empresa y puesto solo se diferencian cuando exactamente uno de los candidatos
contiene un termino profesional conocido. Tambien se admiten dos lineas
consecutivas, una para cada valor. Si la evidencia no basta, ambos campos
quedan en `None`, el bloque completo se conserva en `description` y se genera
una advertencia indexada.

Los rangos de fecha localizados se normalizan sin completar precision ausente.
Las vinetas se conservan en su orden. Una vineta se clasifica como logro si
contiene una medida porcentual o un verbo de resultado conocido; las demas se
tratan como responsabilidades. El texto sin vineta solo permanece en
`description`.

La segmentacion depende de pistas textuales. Varias entradas sin fechas,
separadores ni cargos reconocibles pueden permanecer agrupadas. Un termino
profesional desconocido puede impedir separar empresa y puesto.

## Formacion

Los estudios se separan mediante encabezados estructurados y fechas visibles.
La titulacion y la institucion se identifican con vocabularios limitados en
espanol e ingles, comparados sin distinguir acentos ni mayusculas.

Un rango actual establece `status` como `in_progress`. Una fecha individual se
conserva como `end_date`, ya que no existe evidencia para tratarla como fecha
inicial. Cuando no puede distinguirse institucion y titulacion, los campos
ambiguos quedan en `None`, `description` conserva todas las lineas y el
pipeline registra una advertencia.

## Habilidades

Las listas se separan por coma, punto y coma o barra vertical. Las etiquetas
explicitas, como `Herramientas:`, `Lenguajes de programacion:` o
`Habilidades blandas:`, tienen prioridad sobre el vocabulario.

Sin etiqueta se reconocen vocabularios acotados de lenguajes de programacion,
herramientas y habilidades interpersonales. Un valor desconocido se conserva
en `technical`; no se descarta ni se le asigna un nivel. Los duplicados se
eliminan sin distinguir mayusculas y se conserva la primera clasificacion.
Una etiqueta desconocida genera una advertencia y sus valores se clasifican
individualmente.

## Secciones adicionales

Idiomas:

- se admiten `Idioma: Nivel`, `Idioma - Nivel`, `Idioma | Nivel` y algunos
  niveles finales conocidos;
- una lista sin niveles produce una entrada por idioma;
- un nivel explicito no reconocido se conserva y genera una advertencia.

Certificaciones y cursos:

- la barra vertical separa nombre, institucion y fecha;
- una fecha individual de certificacion se guarda en `date`;
- un curso admite fecha individual o rango, incluido un estado actual;
- mas de dos fragmentos textuales se consideran ambiguos y la linea completa
  se conserva como nombre.

Proyectos:

- las etiquetas `Project`/`Proyecto`, `Description`/`Descripcion`,
  `Technologies`/`Tecnologias` y `URL` agrupan un bloque;
- las tecnologias se separan como una lista y se conserva el orden;
- sin etiquetas, cada linea sigue siendo un proyecto independiente;
- un bloque sin nombre explicito genera una advertencia y no se inventa uno.

## Fechas

Se reconocen anos aislados, combinaciones `YYYY-MM`, `YYYY/MM`, `MM/YYYY` y
meses textuales en espanol o ingles. La salida conserva la precision real:

- mes y ano se representan como `YYYY-MM`;
- un ano aislado permanece como `YYYY`;
- una expresion no reconocida se convierte en `None`.

Los rangos requieren un separador visible: guion, raya, `a`, `hasta`, `to` o
`through`. La comparacion no distingue mayusculas. `Actual`, `Actualidad`,
`Presente`, `Present` y `Current` marcan un periodo vigente.

Una actualidad detectada establece `current=true` en experiencia o
`status="in_progress"` en formacion y cursos. No se deduce actualidad solo por
la ausencia de fecha final.

Para revisar inversiones, una fecha anual se trata como el intervalo enero a
diciembre. Solo se genera una advertencia cuando el comienzo mas temprano es
posterior al final mas tardio. Esta regla evita declarar invertido un rango
como `2024-12` a `2024`, cuya precision no permite esa conclusion.

Las fechas ambiguas quedan en `None` y la advertencia identifica seccion,
indice y campo. Los modelos Pydantic solo aceptan fechas finales con formato
`YYYY` o `YYYY-MM`.

## Deduplicacion

Se elimina una repeticion sin distinguir mayusculas dentro de:

- categorias individuales de habilidades;
- responsabilidades y logros de una experiencia;
- tecnologias de un proyecto;
- listas de advertencias y errores.

Se conserva siempre el primer valor y se genera una advertencia. No se
deduplican experiencias, estudios, idiomas ni `unclassified_text`, porque dos
entradas iguales pueden provenir de posiciones distintas del documento.
