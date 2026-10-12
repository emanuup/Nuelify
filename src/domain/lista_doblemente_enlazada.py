"""
Lista doblemente enlazada para gestionar una playlist.

Cada canción es un nodo que conoce a la canción anterior y a la siguiente,
lo que permite moverse hacia adelante y hacia atrás, e insertar o eliminar
canciones en cualquier posición sin desplazar el resto de la lista.
"""


class Nodo:
    def __init__(self, cancion):
        self.cancion = cancion       # dict con datos de la canción (titulo, artista, ruta...)
        self.anterior = None
        self.siguiente = None


class ListaDoblementeEnlazada:
    def __init__(self):
        self.cabeza = None    # primer nodo de la playlist
        self.cola = None      # último nodo de la playlist
        self.actual = None    # nodo que se está reproduciendo ahora
        self._tamano = 0

    def __len__(self):
        return self._tamano

    def esta_vacia(self):
        return self.cabeza is None

    def agregar_al_final(self, cancion):
        """Agrega una canción al final de la playlist. Costo O(1)."""
        nuevo = Nodo(cancion)
        if self.esta_vacia():
            self.cabeza = nuevo
            self.cola = nuevo
            self.actual = nuevo
        else:
            nuevo.anterior = self.cola
            self.cola.siguiente = nuevo
            self.cola = nuevo
        self._tamano += 1

    def insertar_despues_de_actual(self, cancion):
        """Inserta una canción justo después de la que se está reproduciendo."""
        if self.actual is None:
            self.agregar_al_final(cancion)
            return
        nuevo = Nodo(cancion)
        nuevo.anterior = self.actual
        nuevo.siguiente = self.actual.siguiente
        if self.actual.siguiente:
            self.actual.siguiente.anterior = nuevo
        else:
            self.cola = nuevo
        self.actual.siguiente = nuevo
        self._tamano += 1

    def eliminar(self, nodo):
        """Elimina un nodo específico de la playlist. Costo O(1) si ya tienes el nodo."""
        if nodo.anterior:
            nodo.anterior.siguiente = nodo.siguiente
        else:
            self.cabeza = nodo.siguiente
        if nodo.siguiente:
            nodo.siguiente.anterior = nodo.anterior
        else:
            self.cola = nodo.anterior
        if self.actual is nodo:
            self.actual = nodo.siguiente or nodo.anterior
        self._tamano -= 1

    def siguiente_cancion(self):
        """Avanza a la siguiente canción y la devuelve, o None si ya es la última."""
        if self.actual and self.actual.siguiente:
            self.actual = self.actual.siguiente
            return self.actual.cancion
        return None

    def cancion_anterior(self):
        """Retrocede a la canción anterior y la devuelve, o None si ya es la primera."""
        if self.actual and self.actual.anterior:
            self.actual = self.actual.anterior
            return self.actual.cancion
        return None

    def recorrer(self):
        """Devuelve todas las canciones en orden, de cabeza a cola."""
        canciones = []
        nodo = self.cabeza
        while nodo is not None:
            canciones.append(nodo.cancion)
            nodo = nodo.siguiente
        return canciones


if __name__ == "__main__":
    playlist = ListaDoblementeEnlazada()
    playlist.agregar_al_final({"titulo": "Bohemian Rhapsody", "artista": "Queen"})
    playlist.agregar_al_final({"titulo": "Hotel California", "artista": "Eagles"})
    playlist.agregar_al_final({"titulo": "Imagine", "artista": "John Lennon"})

    print("Playlist completa:")
    for c in playlist.recorrer():
        print(f"  {c['titulo']} - {c['artista']}")

    print("\nActual:", playlist.actual.cancion["titulo"])
    print("Siguiente:", playlist.siguiente_cancion()["titulo"])
    print("Siguiente:", playlist.siguiente_cancion()["titulo"])
    print("Anterior:", playlist.cancion_anterior()["titulo"])