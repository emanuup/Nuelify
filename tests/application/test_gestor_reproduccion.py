"""
Pruebas para el gestor de reproducción.
Ejecutar con: pytest
"""
from application.gestor_reproduccion import GestorReproduccion


def _cancion(titulo):
    return {"titulo": titulo, "artista": "Artista de prueba"}


def test_reproducir_establece_la_cancion_actual():
    gestor = GestorReproduccion()
    resultado = gestor.reproducir(_cancion("A"))

    assert resultado["titulo"] == "A"
    assert gestor.reproduciendo_ahora["titulo"] == "A"


def test_reproducir_manda_la_anterior_al_historial():
    gestor = GestorReproduccion()
    gestor.reproducir(_cancion("A"))
    gestor.reproducir(_cancion("B"))

    assert gestor.historial.ver_ultima()["titulo"] == "A"


def test_siguiente_avanza_en_la_playlist_si_la_cola_esta_vacia():
    gestor = GestorReproduccion()
    gestor.cargar_playlist([_cancion("A"), _cancion("B"), _cancion("C")])
    gestor.reproducir(gestor.playlist_actual.actual.cancion)

    assert gestor.siguiente()["titulo"] == "B"
    assert gestor.siguiente()["titulo"] == "C"
    assert gestor.siguiente() is None  # ya no hay más canciones


def test_la_cola_tiene_prioridad_sobre_la_playlist():
    gestor = GestorReproduccion()
    gestor.cargar_playlist([_cancion("A"), _cancion("B")])
    gestor.reproducir(gestor.playlist_actual.actual.cancion)
    gestor.agregar_a_cola(_cancion("Urgente"))

    assert gestor.siguiente()["titulo"] == "Urgente"


def test_anterior_recupera_del_historial():
    gestor = GestorReproduccion()
    gestor.reproducir(_cancion("A"))
    gestor.reproducir(_cancion("B"))

    assert gestor.anterior()["titulo"] == "A"
    assert gestor.reproduciendo_ahora["titulo"] == "A"


def test_anterior_sin_historial_devuelve_none():
    gestor = GestorReproduccion()
    assert gestor.anterior() is None