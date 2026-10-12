"""
Pruebas para la pila de historial.
Ejecutar con: pytest
"""
from domain.pila_historial import PilaHistorial


def _cancion(titulo):
    return {"titulo": titulo, "artista": "Artista de prueba"}


def test_pila_vacia_al_crear():
    historial = PilaHistorial()
    assert historial.esta_vacia()
    assert len(historial) == 0


def test_apilar_guarda_en_orden_inverso():
    historial = PilaHistorial()
    historial.apilar(_cancion("A"))
    historial.apilar(_cancion("B"))
    historial.apilar(_cancion("C"))

    assert [c["titulo"] for c in historial.recorrer()] == ["C", "B", "A"]


def test_desapilar_devuelve_la_ultima_reproducida_primero():
    historial = PilaHistorial()
    historial.apilar(_cancion("A"))
    historial.apilar(_cancion("B"))

    assert historial.desapilar()["titulo"] == "B"
    assert historial.desapilar()["titulo"] == "A"
    assert historial.desapilar() is None  # ya está vacía
    assert historial.esta_vacia()


def test_ver_ultima_no_saca_la_cancion_de_la_pila():
    historial = PilaHistorial()
    historial.apilar(_cancion("A"))

    assert historial.ver_ultima()["titulo"] == "A"
    assert len(historial) == 1  # sigue en la pila