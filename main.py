"""
Punto de entrada del launcher de música.

Ejecutar con:  python main.py
"""

import os
import sys

# Permite importar los módulos que están dentro de src/
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from presentation.ventana_web import iniciar

if __name__ == "__main__":
    iniciar()