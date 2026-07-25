# Changelog

Este archivo registra los cambios relevantes del proyecto.

## Unreleased

Sin cambios registrados.

## 0.1.0 - 2026-07-24

### Added

- Estructura modular del paquete `cv_analyzer`.
- Validacion de extension, ruta, tamano, cifrado y contenido extraible.
- Lectura de texto y metadatos PDF mediante PyMuPDF.
- Limpieza de texto y deteccion de secciones en espanol e ingles.
- Extractores de datos personales, contacto, experiencia, formacion,
  habilidades, idiomas, certificaciones, cursos y proyectos.
- Normalizacion inicial de fechas y advertencias de consistencia.
- Modelos Pydantic y contrato JSON estable para resultados correctos y fallidos.
- Pipeline central con registro tecnico y manejo controlado de errores.
- Interfaz Streamlit con carga, estado, vistas y descarga JSON.
- Helpers para archivos temporales, nombres seguros y serializacion.
- Pruebas unitarias, integracion simulada y recorridos con PDFs sinteticos.
- Casos para documentos vacios, corruptos, cifrados, sin encabezados y con
  secciones duplicadas.
- Cobertura de ramas configurada con un umbral minimo del 80%.
- Ejemplo ejecutable y resultado JSON de referencia con datos ficticios.
- Documentacion de instalacion, arquitectura, esquema, pruebas, limitaciones,
  mejoras y memoria tecnica.
- Licencia MIT.

### Fixed

- Deteccion de PDFs protegidos y errores de lectura.
- Conservacion del contenido de secciones duplicadas con advertencia.
- Falsos positivos que trataban datos de contacto como titulo profesional.
- Falsos positivos que trataban fragmentos de correo como URLs de portfolio.
- Reconocimiento del encabezado ingles simple `EXPERIENCE`.
