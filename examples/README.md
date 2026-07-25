# Ejemplos

Los archivos de este directorio usan exclusivamente datos ficticios.

## Ejemplo ejecutable

Desde la raiz del repositorio y con el proyecto instalado:

```powershell
python examples/run_example.py
```

El script:

1. Lee `sample_cv.txt`.
2. Genera un PDF dentro de un directorio temporal.
3. Ejecuta el pipeline real.
4. Elimina el PDF al cerrar el contexto temporal.
5. Escribe el resultado en `examples/output/sample_result.json`.

La carpeta `output` esta ignorada por Git. Puede eliminarse sin afectar al
proyecto.

## Resultado de referencia

`example_result.json` muestra el contrato completo con valores representativos
y una marca temporal fija. Sirve para inspeccionar la estructura; la ejecucion
real genera sus propios metadatos de archivo y tiempo.
