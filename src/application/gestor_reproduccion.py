"""
Gestor de reproducción: capa de aplicación que conecta la playlist actual
(lista doblemente enlazada), la cola de reproducción y el historial, para
ofrecer las acciones que el usuario dispara desde la interfaz: reproducir,
saltar a la siguiente, volver a la anterior, etc.
"""

from domain.lista_doblemente_enlazada import ListaDoblementeEnlazada
from domain.cola_reproduccion import ColaReproduccion
from domain.pila_historial import PilaHistorial


class GestorReproduccion:
    def __init__(self):
        self.playlist_actual = ListaDoblementeEnlazada()
        self.cola = ColaReproduccion()
        self.historial = PilaHistorial()
        self.reproduciendo_ahora = None

    def cargar_playlist(self, canciones):
        """Reemplaza la playlist actual por una nueva lista de canciones."""
        self.playlist_actual = ListaDoblementeEnlazada()
        for cancion in canciones:
            self.playlist_actual.agregar_al_final(cancion)

    def agregar_a_cola(self, cancion):
        """El usuario eligió 'reproducir a continuación'."""
        self.cola.encolar(cancion)

    def reproducir(self, cancion):
        """
        Empieza a reproducir una canción. Si ya había algo sonando, lo
        manda primero al historial, antes de reemplazarlo.
        """
        if self.reproduciendo_ahora is not None:
            self.historial.apilar(self.reproduciendo_ahora)
        self.reproduciendo_ahora = cancion
        return cancion

    def siguiente(self):
        """
        Decide qué suena después: la cola tiene prioridad sobre la
        playlist, porque el usuario la pidió explícitamente con
        'reproducir a continuación'. Si la cola está vacía, sigue
        avanzando en la playlist normal.
        """
        if not self.cola.esta_vacia():
            return self.reproducir(self.cola.desencolar())

        siguiente_cancion = self.playlist_actual.siguiente_cancion()
        if siguiente_cancion is not None:
            return self.reproducir(siguiente_cancion)

        return None  # no queda nada más por reproducir

    def anterior(self):
        """Vuelve a la última canción reproducida, según el historial."""
        cancion_anterior = self.historial.desapilar()
        if cancion_anterior is not None:
            self.reproduciendo_ahora = cancion_anterior
        return cancion_anterior


if __name__ == "__main__":
    gestor = GestorReproduccion()
    gestor.cargar_playlist([
        {"titulo": "Bohemian Rhapsody", "artista": "Queen"},
        {"titulo": "Hotel California", "artista": "Eagles"},
    ])

    print("Reproduce:", gestor.reproducir(gestor.playlist_actual.actual.cancion)["titulo"])
    print("Siguiente:", gestor.siguiente()["titulo"])

    gestor.agregar_a_cola({"titulo": "Imagine", "artista": "John Lennon"})
    print("Siguiente (debería ser la de la cola):", gestor.siguiente()["titulo"])

    print("Anterior:", gestor.anterior()["titulo"])