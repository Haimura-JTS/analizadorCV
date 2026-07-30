# Informe final

## Ficha del proyecto

| Campo | Resultado |
| --- | --- |
| Proyecto | Analizador de CV |
| Version de entrega | 0.2.0 |
| Contrato de procesamiento | 1.0 |
| Lenguaje | Python 3.11 o superior |
| Interfaz | Streamlit |
| Lectura PDF | PyMuPDF |
| Validacion | Pydantic |
| Pruebas | pytest y pytest-cov |
| Licencia | MIT |

## Resumen

El proyecto entrega una aplicacion local capaz de recibir un curriculum PDF
con capa de texto, validar el documento, extraer y normalizar su contenido,
detectar secciones, estructurar informacion y producir un JSON consistente.

La misma logica puede utilizarse desde Streamlit o desde la API Python. El
pipeline no depende de la interfaz y siempre intenta devolver el contrato
completo, tambien cuando el documento es invalido o una fase falla.

El desarrollo se realizo de forma incremental en las etapas 0 a 10. Cada
etapa incorporo revision tecnica, pruebas y documentacion antes de continuar.

## Objetivos alcanzados

- Carga manual o mediante arrastre de un unico PDF.
- Validacion de extension, existencia, tamano y contenido.
- Deteccion de documentos vacios, corruptos, protegidos o escaneados.
- Extraccion de texto y metadatos por pagina.
- Limpieza conservadora de espacios, controles y caracteres invisibles.
- Datos personales y contacto sin completar valores ausentes.
- Secciones en espanol e ingles, incluidas variantes decoradas.
- Experiencia, formacion, habilidades y secciones adicionales.
- Fechas parciales y periodos actuales sin inventar precision.
- Validacion estricta del resultado mediante Pydantic.
- JSON descargable con advertencias, errores y texto no clasificado.
- Manejo controlado de fallos y logging sin contenido personal.
- Pruebas unitarias, integrales, de interfaz y de documentacion.

## Arquitectura entregada

La solucion mantiene dependencias dirigidas hacia el pipeline:

```text
Streamlit / API Python
          |
          v
       pipeline
          |
          +--> pdf_reader
          +--> text_cleaner
          +--> section_detector
          +--> extractores
          +--> json_builder
          `--> validators --> modelos Pydantic
```

`app.py` gestiona carga, estado y presentacion. Los modulos de
`src/cv_analyzer` contienen lectura, heuristicas, construccion y validacion.
Las responsabilidades completas se describen en
[architecture.md](architecture.md).

## Flujo de datos

1. El cliente proporciona una ruta PDF.
2. El lector valida archivo, paginas y texto extraible.
3. El limpiador normaliza el texto sin interpretar su significado.
4. Se extraen contacto y datos iniciales.
5. El detector agrupa lineas por seccion y conserva texto no clasificado.
6. Los extractores crean entradas estructuradas y advertencias.
7. El constructor ensambla el contrato.
8. Los validadores normalizan fechas, revisan coherencia y aplican Pydantic.
9. El pipeline devuelve JSON y, cuando se solicita, texto extraido.
10. Streamlit presenta resumen, texto, JSON y descarga.

## Decisiones tecnicas

### PyMuPDF

Se eligio por su API sencilla, velocidad, lectura por paginas y capacidad para
crear fixtures PDF. La consecuencia conocida es que documentos escaneados
requieren OCR y ciertos layouts pueden alterar el orden de lectura. La
decision se detalla en [decisions/0001-pymupdf.md](decisions/0001-pymupdf.md).

### Heuristicas explicitas

La extraccion utiliza reglas visibles y conservadoras en lugar de depender de
IA o servicios externos. Cuando no existe evidencia suficiente, el campo queda
en `null` o se genera una advertencia. Las reglas se documentan en
[heuristics.md](heuristics.md).

### Contrato estable

Exito y error comparten la misma estructura. Las colecciones repetibles usan
listas, los datos ausentes usan `null` y los diagnosticos viven en metadata.
El contrato completo esta en [json_schema.md](json_schema.md).

## Calidad y pruebas

La verificacion final se realizo con Python 3.13.5:

- 175 casos recopilados;
- 175 casos correctos;
- 0 fallos;
- 94,91% de cobertura total del paquete;
- umbral minimo configurado del 80%;
- 142 funciones de prueba mas variantes parametrizadas.

La matriz incluye PDFs en espanol e ingles, una y dos columnas, varias
experiencias, secciones ausentes, iconos, fechas alternativas, encabezados
desconocidos o duplicados y documentos invalidos. Todos los recorridos reales
validan el resultado con `CVResultModel`.

Streamlit tambien fue verificado con `AppTest` y mediante un recorrido local
responsive en Chrome. Los detalles se encuentran en [testing.md](testing.md).

## Privacidad y seguridad

- El procesamiento es local y no consulta servicios externos.
- Los PDFs de la interfaz se eliminan al finalizar el contexto temporal.
- No se registran nombres, contacto ni contenido completo del curriculum.
- Los errores de sistema no exponen rutas privadas.
- Ejemplos y fixtures usan identidades y dominios ficticios.
- `.env`, secretos, logs, caches, PDFs de entrada y salidas generadas estan
  excluidos del control de versiones.
- No existe base de datos, autenticacion ni almacenamiento de historicos.

## Dificultades y soluciones

| Dificultad | Solucion aplicada |
| --- | --- |
| PDFs vacios, cifrados o escaneados | Excepciones de dominio y salida contractual |
| Encabezados variables | Alias normalizados sin coincidencias parciales |
| Datos ambiguos | `null`, descripcion conservada y advertencia indexada |
| Fechas con distinta precision | Comparacion por limites sin completar meses |
| Secciones duplicadas | Acumulacion de contenido y advertencia |
| Fallos posteriores a la lectura | Conservacion de texto y metadatos conocidos |
| Errores con rutas privadas | Traduccion segura por tipo de error |
| Interfaz extensa en movil | Layout responsive y descarga en cabecera |

## Limitaciones

- No se aplica OCR.
- El orden de lectura puede variar en PDFs con geometria compleja.
- Los vocabularios de puestos, estudios y habilidades son deliberadamente
  limitados.
- Solo se conserva la primera coincidencia de cada tipo de contacto.
- No se interpretan dias, trimestres ni fechas aproximadas.
- La prueba de dos columnas representa un caso sencillo, no todos los layouts.
- No se mide precision estadistica porque no existe un corpus anonimizado.

El inventario detallado se mantiene en [limitations.md](limitations.md).

## Reproduccion

Desde una copia nueva del repositorio:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m pip check
python -m pytest
python examples/run_example.py
python -m streamlit run app.py
```

El resultado de referencia se encuentra en
[`../examples/example_result.json`](../examples/example_result.json).

## Lista de entrega

- [x] Paquete instalable.
- [x] Interfaz funcional.
- [x] API reutilizable.
- [x] Contrato JSON documentado.
- [x] Ejemplo reproducible.
- [x] Errores controlados.
- [x] Datos ficticios.
- [x] Suite automatizada.
- [x] Cobertura superior al umbral.
- [x] README y guia de instalacion.
- [x] Arquitectura, heuristicas y decisiones.
- [x] Changelog, memoria, limitaciones y mejoras.
- [x] Licencia MIT.

## Evolucion futura

Las mejoras propuestas incluyen OCR local, reconstruccion avanzada del orden
de lectura, corpus anonimizado, edicion previa a descarga y automatizacion de
calidad. Deben desarrollarse como un nuevo ciclo sin romper el contrato 1.0.
La priorizacion esta en [improvements.md](improvements.md).

## Conclusion

La version 0.2.0 cumple el alcance academico obligatorio con una arquitectura
modular, contrato estable, tratamiento conservador de la informacion y una
base de pruebas reproducible. El proyecto queda preparado para entrega y para
ampliaciones posteriores desacopladas.
