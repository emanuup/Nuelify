"""
Pruebas para la lista doblemente enlazada de playlists.
Ejecutar con: pytest
"""
from domain.lista_doblemente_enlazada import ListaDoblementeEnlazada


def _cancion(titulo):
    return {"titulo": titulo, "artista": "Artista de prueba"}


def test_lista_vacia_al_crear():
    playlist = ListaDoblementeEnlazada()
    assert playlist.esta_vacia()
    assert len(playlist) == 0


def test_agregar_al_final_respeta_el_orden():
    playlist = ListaDoblementeEnlazada()
    playlist.agregar_al_final(_cancion("A"))
    playlist.agregar_al_final(_cancion("B"))
    playlist.agregar_al_final(_cancion("C"))

    titulos = [c["titulo"] for c in playlist.recorrer()]
    assert titulos == ["A", "B", "C"]
    assert len(playlist) == 3


def test_siguiente_y_anterior_navegan_correctamente():
    playlist = ListaDoblementeEnlazada()
    playlist.agregar_al_final(_cancion("A"))
    playlist.agregar_al_final(_cancion("B"))
    playlist.agregar_al_final(_cancion("C"))

    assert playlist.actual.cancion["titulo"] == "A"
    assert playlist.siguiente_cancion()["titulo"] == "B"
    assert playlist.siguiente_cancion()["titulo"] == "C"
    assert playlist.siguiente_cancion() is None  # ya no hay más canciones
    assert playlist.cancion_anterior()["titulo"] == "B"


def test_insertar_despues_de_actual():
    playlist = ListaDoblementeEnlazada()
    playlist.agregar_al_final(_cancion("A"))
    playlist.agregar_al_final(_cancion("C"))
    playlist.insertar_despues_de_actual(_cancion("B"))  # actual sigue siendo A

    titulos = [c["titulo"] for c in playlist.recorrer()]
    assert titulos == ["A", "B", "C"]


def test_eliminar_nodo_intermedio():
    playlist = ListaDoblementeEnlazada()
    playlist.agregar_al_final(_cancion("A"))
    playlist.agregar_al_final(_cancion("B"))
    playlist.agregar_al_final(_cancion("C"))

    nodo_b = playlist.cabeza.siguiente
    playlist.eliminar(nodo_b)

    titulos = [c["titulo"] for c in playlist.recorrer()]
    assert titulos == ["A", "C"]
    assert len(playlist) == 2