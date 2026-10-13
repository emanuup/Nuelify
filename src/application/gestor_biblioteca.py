"""
Gestor de biblioteca: capa de aplicación que conecta la tabla hash del
dominio con la lectura de archivos y la persistencia, para ofrecer
operaciones de alto nivel como "cargar toda la música de una carpeta"
o "buscar una canción por nombre".
"""
import os
import sys
from pathlib import Path
from domain.tabla_hash import TablaHash
from infrastructure.lector_metadatos import escanear_carpeta
from infrastructure.gestor_persistencia import guardar, cargar

def _carpeta_datos():
    """Carpeta del usuario donde vive la biblioteca guardada."""
    if sys.platform.startswith("win"):
        base = Path(os.environ.get("APPDATA", Path.home()))
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    carpeta = base / "Nuelify"
    carpeta.mkdir(parents=True, exist_ok=True)
    return carpeta


RUTA_BIBLIOTECA_GUARDADA = str(_carpeta_datos() / "biblioteca.json")


class GestorBiblioteca:
    def __init__(self):
        self.indice = TablaHash()

    def cargar_desde_carpeta(self, ruta_carpeta):
        """
        Escanea una carpeta en busca de música y la agrega al índice.
        Cada canción se guarda bajo una clave única basada en su ruta de
        archivo, así que volver a escanear la misma carpeta actualiza
        en vez de duplicar canciones.
        """
        canciones = escanear_carpeta(ruta_carpeta)
        for cancion in canciones:
            self.indice.insertar(cancion["ruta"], cancion)
        return len(canciones)

    def buscar_por_titulo(self, texto_busqueda):
        """
        Busca canciones cuyo título contenga el texto, sin importar
        mayúsculas/minúsculas. Recorre toda la biblioteca (no es tan
        rápida como buscar por clave exacta), pero sirve para que el
        usuario escriba solo parte del nombre en la barra de búsqueda.
        """
        texto_busqueda = texto_busqueda.lower()
        return [
            cancion for cancion in self.indice.todas_las_canciones()
            if texto_busqueda in cancion["titulo"].lower()
        ]

    def todas(self):
        return self.indice.todas_las_canciones()

    def guardar(self, ruta_archivo=RUTA_BIBLIOTECA_GUARDADA):
        guardar(self.indice.todas_las_canciones(), ruta_archivo)

    def cargar(self, ruta_archivo=RUTA_BIBLIOTECA_GUARDADA):
        """Restaura la biblioteca guardada anteriormente, si existe."""
        canciones = cargar(ruta_archivo, valor_por_defecto=[])
        for cancion in canciones:
            self.indice.insertar(cancion["ruta"], cancion)
        return len(canciones)


if __name__ == "__main__":
    gestor = GestorBiblioteca()
    total = gestor.cargar_desde_carpeta("data")
    print(f"Se indexaron {total} canciones desde 'data'.")

    resultados = gestor.buscar_por_titulo("jean")
    print(f"Resultados para 'jean': {len(resultados)}")

    gestor.guardar()
    print("Biblioteca guardada.")