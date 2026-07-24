"""
Configuracion general del proyecto.

Centraliza valores modificables utilizados por distintos modulos. No contiene
logica de extraccion ni reglas heuristicas de interpretacion del curriculum.
"""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024

