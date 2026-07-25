# Memoria tecnica

## Resumen

Analizador de CV es una aplicacion academica local que transforma el contenido
textual de un curriculum PDF en un JSON estable. El proyecto prioriza reglas
comprensibles, conservacion de informacion y separacion de responsabilidades.

## Problema

Los curriculums combinan formatos visuales, idiomas y encabezados diferentes.
Una aplicacion consumidora necesita una estructura predecible sin asumir que
todos los documentos contienen los mismos campos.

La solucion debe distinguir entre:

- ausencia de informacion;
- contenido ambiguo;
- advertencias de calidad;
- errores que impiden procesar el archivo.

## Objetivos

- Procesar PDFs textuales de forma local.
- Detectar secciones habituales en espanol e ingles.
- Construir un JSON validado y serializable.
- No inventar campos ausentes.
- Mantener el mismo contrato ante errores.
- Ofrecer una interfaz sencilla y una API reutilizable.
- Documentar limites y decisiones tecnicas.

## Alcance de la version 0.1.0

La version incluye lectura PDF, limpieza, deteccion de secciones, extractores
conservadores, normalizacion inicial de fechas, validacion Pydantic, pipeline,
interfaz Streamlit, pruebas, ejemplos y documentacion.

Quedan fuera OCR, interpretacion semantica avanzada, persistencia, servicios
externos y procesamiento por lotes.

## Metodologia

El desarrollo se dividio en diez etapas:

1. Estructura y alcance.
2. Lectura y validacion PDF.
3. Limpieza y datos basicos.
4. Deteccion de secciones.
5. Extraccion estructurada.
6. Fechas, modelos y validacion.
7. Pipeline completo.
8. Interfaz Streamlit.
9. Pruebas y robustez.
10. Documentacion y entrega.

Cada etapa mantuvo responsabilidades pequenas y un commit identificable.

## Arquitectura

La interfaz llama a un unico pipeline. Este coordina modulos especializados,
construye el resultado y lo valida antes de devolverlo. La arquitectura evita
que Streamlit conozca expresiones regulares, reglas de fechas o detalles de
PyMuPDF.

Los modelos Pydantic constituyen el limite contractual. La salida fallida usa
los mismos modelos que una salida correcta, lo que simplifica a los clientes.

## Decisiones tecnicas

### Python 3.11

Permite tipado moderno como `str | None` y cuenta con un ecosistema adecuado
para PDF, validacion y pruebas.

### PyMuPDF

Se utiliza para abrir documentos, extraer texto, contar paginas y crear PDFs
sinteticos en las pruebas.

### Pydantic

Valida tipos, valores por defecto y campos inesperados. Evita que una
modificacion interna altere silenciosamente el contrato.

### Streamlit

Proporciona una interfaz local con carga por seleccion o arrastre, estado,
vistas y descarga sin introducir un backend adicional.

### Heuristicas conservadoras

Los extractores asignan valores solo cuando una regla visible lo permite. El
contenido ambiguo permanece en descripciones, nombres o texto no clasificado.

## Flujo principal

1. Validar el archivo.
2. Extraer texto y metadatos.
3. Limpiar y dividir lineas.
4. Detectar datos iniciales y secciones.
5. Ejecutar extractores especializados.
6. Construir el diccionario.
7. Normalizar fechas y generar advertencias.
8. Validar con `CVResultModel`.
9. Devolver datos y texto disponible.

## Robustez

El lector distingue archivos inexistentes, extensiones invalidas, rutas que
son directorios, exceso de tamano, cifrado, falta de texto y contenido
corrupto. El pipeline convierte errores esperados en mensajes publicos y
registra los inesperados sin exponer su detalle.

Las secciones duplicadas acumulan contenido y generan una advertencia. Los
fragmentos de correo se excluyen de la deteccion de URLs, y los contactos no
se aceptan como titulo profesional.

## Pruebas

La suite combina:

- pruebas unitarias por modulo;
- integracion con lectura simulada;
- PDFs sinteticos procesados por el recorrido real;
- estados de Streamlit con `AppTest`;
- validacion del ejemplo documentado;
- casos correctos y fallidos con el mismo modelo.

`pytest-cov` esta configurado para cobertura de ramas y un minimo del 80% en
`cv_analyzer`. La ejecucion final con Python 3.13.5 completo 75 casos y alcanzo
una cobertura total observada del 93,36%.

## Privacidad

El procesamiento no consulta servicios externos. Los archivos cargados se
copian a un directorio temporal y se eliminan al finalizar. Las pruebas y los
ejemplos usan identidades ficticias y dominios reservados para demostracion.

## Resultados

El proyecto entrega:

- paquete Python instalable;
- interfaz Streamlit;
- API de procesamiento;
- contrato JSON documentado;
- manejo de errores consistente;
- ejemplos reproducibles;
- suite de pruebas con cobertura configurada;
- documentacion tecnica y de usuario.

## Limitaciones

Los escaneos requieren OCR, los layouts complejos pueden alterar el orden del
texto y cada bloque de experiencia o formacion se agrupa en una unica entrada.
El detalle completo se mantiene en
[`limitations.md`](limitations.md).

## Conclusion

La version 0.1.0 establece una base modular y auditable. La siguiente evolucion
debe centrarse en OCR, separacion de entradas y medicion de precision sin
sacrificar el contrato ni la conservacion de informacion.
