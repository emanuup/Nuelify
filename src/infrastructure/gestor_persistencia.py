"""
Gestor de persistencia: guarda y carga datos del launcher en formato JSON.

Se usa para que la biblioteca musical y las playlists no se pierdan
cada vez que se cierra el programa.
"""

import json
import os


def guardar(datos, ruta_archivo):
    """
    Guarda datos (listas, diccionarios) en un archivo JSON.
    Si la carpeta del archivo no existe todavía, la crea.
    """
    carpeta = os.path.dirname(ruta_archivo)
    if carpeta:
        os.makedirs(carpeta, exist_ok=True)

    with open(ruta_archivo, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, indent=2, ensure_ascii=False)


def cargar(ruta_archivo, valor_por_defecto=None):
    """
    Carga datos desde un archivo JSON. Si el archivo no existe todavía
    (por ejemplo, la primera vez que se abre el programa) o quedó
    corrupto, devuelve valor_por_defecto en vez de fallar.
    """
    if not os.path.exists(ruta_archivo):
        return valor_por_defecto

    try:
        with open(ruta_archivo, "r", encoding="utf-8") as archivo:
            return json.load(archivo)
    except json.JSONDecodeError:
        return valor_por_defecto


if __name__ == "__main__":
    canciones_de_prueba = [
        {"titulo": "Billie Jean", "artista": "Michael Jackson"},
        {"titulo": "Like a Prayer", "artista": "Madonna"},
    ]

    guardar(canciones_de_prueba, "data/biblioteca_prueba.json")
    print("Guardado en data/biblioteca_prueba.json")

    canciones_cargadas = cargar("data/biblioteca_prueba.json", valor_por_defecto=[])
    print(f"Se cargaron {len(canciones_cargadas)} canciones:")
    for c in canciones_cargadas:
        print(f"  {c['titulo']} - {c['artista']}")