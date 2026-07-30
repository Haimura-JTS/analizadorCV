# ADR 0001: uso de PyMuPDF para extraer texto

## Estado

Aceptada.

## Contexto

El analizador necesita abrir curriculums PDF, comprobar si estan protegidos,
recorrer sus paginas y extraer texto sin enviar datos personales a servicios
externos. La biblioteca debe funcionar desde el pipeline y desde las pruebas,
sin depender de Streamlit.

## Opciones consideradas

- PyMuPDF: API directa, buen rendimiento y acceso a paginas y metadatos.
- pdfplumber: util para tablas y disposiciones visuales, con una capa adicional
  sobre pdfminer.six.
- pdfminer.six: flexible para analisis de bajo nivel, pero mas complejo para el
  alcance academico inicial.
- pypdf: adecuado para estructura y manipulacion, con extraccion de texto menos
  orientada al recorrido visual del documento.

## Decision

Utilizar PyMuPDF como unica dependencia de lectura PDF en la version `0.1.x`.

La decision reduce el numero de dependencias y permite usar la misma biblioteca
para generar PDFs sinteticos en las pruebas. Todo el procesamiento permanece
en el equipo local.

## Consecuencias

- Los PDF con capa de texto pueden procesarse pagina a pagina.
- Los documentos protegidos se detectan antes de extraer contenido.
- El orden de lectura puede ser impreciso en documentos con varias columnas.
- Un PDF basado solo en imagenes requiere OCR, que queda fuera del alcance
  inicial.
- Sustituir la biblioteca afectaria principalmente a `pdf_reader.py` y a las
  fabricas de PDF de las pruebas, no al contrato JSON.

## Verificacion

`tests/unit/test_pdf_reader.py` contiene una prueba que genera un PDF temporal,
extrae su texto y comprueba paginas, tamano y advertencias. Los recorridos
completos se cubren en `tests/integration/test_real_pdf_pipeline.py`.
