"""
Cola de reproducción: gestiona las canciones que se van a reproducir a continuación.

Es una estructura FIFO (primero en entrar, primero en salir): la primera canción
que se agrega es la primera que se reproduce.
"""


class NodoCola:
    def __init__(self, cancion):
        self.cancion = cancion
        self.siguiente = None


class ColaReproduccion:
    def __init__(self):
        self.frente = None    # próxima canción a reproducir
        self.final = None     # última canción agregada
        self._tamano = 0

    def __len__(self):
        return self._tamano

    def esta_vacia(self):
        return self.frente is None

    def encolar(self, cancion):
        """Agrega una canción al final de la cola. Costo O(1)."""
        nuevo = NodoCola(cancion)
        if self.esta_vacia():
            self.frente = nuevo
            self.final = nuevo
        else:
            self.final.siguiente = nuevo
            self.final = nuevo
        self._tamano += 1

    def desencolar(self):
        """Saca y devuelve la próxima canción a reproducir. Costo O(1)."""
        if self.esta_vacia():
            return None
        nodo = self.frente
        self.frente = nodo.siguiente
        if self.frente is None:
            self.final = None
        self._tamano -= 1
        return nodo.cancion

    def ver_siguiente(self):
        """Muestra cuál es la próxima canción sin sacarla de la cola."""
        return self.frente.cancion if self.frente else None

    def recorrer(self):
        """Devuelve las canciones en espera, en orden de reproducción."""
        canciones = []
        nodo = self.frente
        while nodo is not None:
            canciones.append(nodo.cancion)
            nodo = nodo.siguiente
        return canciones


if __name__ == "__main__":
    cola = ColaReproduccion()
    cola.encolar({"titulo": "Come as You Are", "artista": "Nirvana"})
    cola.encolar({"titulo": "Losing My Religion", "artista": "R.E.M."})
    cola.encolar({"titulo": "Creep", "artista": "Radiohead"})

    print("En espera:")
    for c in cola.recorrer():
        print(f"  {c['titulo']} - {c['artista']}")

    print("\nSiguiente a reproducir:", cola.ver_siguiente()["titulo"])
    print("Se reproduce:", cola.desencolar()["titulo"])
    print("Ahora sigue:", cola.ver_siguiente()["titulo"])