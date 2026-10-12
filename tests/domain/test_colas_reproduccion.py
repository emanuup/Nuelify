"""
Pruebas para la cola de reproducción.
Ejecutar con: pytest
"""
from domain.cola_reproduccion import ColaReproduccion


def _cancion(titulo):
    return {"titulo": titulo, "artista": "Artista de prueba"}


def test_cola_vacia_al_crear():
    cola = ColaReproduccion()
    assert cola.esta_vacia()
    assert len(cola) == 0


def test_encolar_respeta_orden_de_llegada():
    cola = ColaReproduccion()
    cola.encolar(_cancion("A"))
    cola.encolar(_cancion("B"))
    cola.encolar(_cancion("C"))

    assert [c["titulo"] for c in cola.recorrer()] == ["A", "B", "C"]


def test_desencolar_devuelve_en_orden_fifo():
    cola = ColaReproduccion()
    cola.encolar(_cancion("A"))
    cola.encolar(_cancion("B"))

    assert cola.desencolar()["titulo"] == "A"
    assert cola.desencolar()["titulo"] == "B"
    assert cola.desencolar() is None  # ya está vacía
    assert cola.esta_vacia()


def test_ver_siguiente_no_saca_la_cancion_de_la_cola():
    cola = ColaReproduccion()
    cola.encolar(_cancion("A"))

    assert cola.ver_siguiente()["titulo"] == "A"
    assert len(cola) == 1  # sigue en la cola