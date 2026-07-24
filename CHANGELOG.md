# Changelog

## Unreleased

- Se crea la estructura inicial del proyecto.
- Se documenta el alcance inicial.
- Se anade una primera funcion para extraer texto de PDF.
- Se refuerza la validacion de PDF con tamano maximo, rutas invalidas,
  documentos protegidos, documentos vacios y errores de lectura controlados.
- Se anaden limpieza de texto, extraccion de contacto, heuristica inicial de
  datos personales y construccion de JSON basico.
- Se anade deteccion de secciones principales con aliases en espanol e ingles,
  texto no clasificado y advertencias por secciones duplicadas.
- Se anaden extractores iniciales para experiencia, formacion, habilidades,
  idiomas, certificaciones, cursos y proyectos.
- Se anaden normalizacion de fechas, modelos Pydantic y validacion con
  advertencias.
- Se conecta el flujo completo mediante un pipeline con metadatos, registro
  tecnico, manejo centralizado de errores y salida JSON consistente.
- Se anaden pruebas de integracion para recorridos correctos, errores de
  archivo, fallos inesperados y resultados intermedios invalidos.
- Se anade una interfaz Streamlit con carga por seleccion o arrastre, estado
  del procesamiento, vistas de resumen, texto y JSON, y descarga del resultado.
- Se incorpora una respuesta detallada del pipeline para reutilizar el texto
  extraido sin leer dos veces el PDF.
- Se anaden manejo seguro de archivos temporales, configuracion visual y
  pruebas unitarias de los helpers de presentacion.
