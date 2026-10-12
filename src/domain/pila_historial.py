"""
Pila de historial: guarda las canciones que ya se reprodujeron.

Es una estructura LIFO (último en entrar, primero en salir): la última
canción reproducida es la primera que aparece al usar el botón "anterior".
"""


class NodoPila:
    def __init__(self, cancion):
        self.cancion = cancion
        self.siguiente = None


class PilaHistorial:
    def __init__(self):
        self.tope = None      # última canción reproducida
        self._tamano = 0

    def __len__(self):
        return self._tamano

    def esta_vacia(self):
        return self.tope is None

    def apilar(self, cancion):
        """Registra una canción como recién reproducida. Costo O(1)."""
        nuevo = NodoPila(cancion)
        nuevo.siguiente = self.tope
        self.tope = nuevo
        self._tamano += 1

    def desapilar(self):
        """Saca y devuelve la última canción reproducida (botón 'anterior'). Costo O(1)."""
        if self.esta_vacia():
            return None
        nodo = self.tope
        self.tope = nodo.siguiente
        self._tamano -= 1
        return nodo.cancion

    def ver_ultima(self):
        """Muestra cuál fue la última canción reproducida sin sacarla de la pila."""
        return self.tope.cancion if self.tope else None

    def recorrer(self):
        """Devuelve el historial completo, de la más reciente a la más antigua."""
        canciones = []
        nodo = self.tope
        while nodo is not None:
            canciones.append(nodo.cancion)
            nodo = nodo.siguiente
        return canciones


if __name__ == "__main__":
    historial = PilaHistorial()
    historial.apilar({"titulo": "Wonderwall", "artista": "Oasis"})
    historial.apilar({"titulo": "Zombie", "artista": "The Cranberries"})
    historial.apilar({"titulo": "Numb", "artista": "Linkin Park"})

    print("Historial (de más reciente a más antigua):")
    for c in historial.recorrer():
        print(f"  {c['titulo']} - {c['artista']}")

    print("\nÚltima reproducida:", historial.ver_ultima()["titulo"])
    print("Vuelve a sonar:", historial.desapilar()["titulo"])
    print("Ahora la última es:", historial.ver_ultima()["titulo"])