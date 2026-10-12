"""
Pruebas para la tabla hash de la biblioteca musical.
Ejecutar con: pytest
"""
from domain.tabla_hash import TablaHash


def _cancion(titulo):
    return {"titulo": titulo, "artista": "Artista de prueba"}


def test_tabla_vacia_al_crear():
    biblioteca = TablaHash()
    assert len(biblioteca) == 0


def test_insertar_y_buscar():
    biblioteca = TablaHash()
    biblioteca.insertar("001", _cancion("A"))

    assert biblioteca.buscar("001")["titulo"] == "A"
    assert len(biblioteca) == 1


def test_buscar_clave_inexistente_devuelve_none():
    biblioteca = TablaHash()
    assert biblioteca.buscar("no-existe") is None


def test_insertar_misma_clave_actualiza_en_vez_de_duplicar():
    biblioteca = TablaHash()
    biblioteca.insertar("001", _cancion("Version vieja"))
    biblioteca.insertar("001", _cancion("Version nueva"))

    assert biblioteca.buscar("001")["titulo"] == "Version nueva"
    assert len(biblioteca) == 1


def test_eliminar_quita_la_cancion():
    biblioteca = TablaHash()
    biblioteca.insertar("001", _cancion("A"))

    assert biblioteca.eliminar("001") is True
    assert biblioteca.buscar("001") is None
    assert len(biblioteca) == 0


def test_eliminar_clave_inexistente_devuelve_false():
    biblioteca = TablaHash()
    assert biblioteca.eliminar("no-existe") is False


def test_maneja_colisiones_forzadas():
    # capacidad chica a propósito para forzar que varias claves caigan en la misma cubeta
    biblioteca = TablaHash(capacidad=2)
    biblioteca.insertar("a", _cancion("Cancion A"))
    biblioteca.insertar("b", _cancion("Cancion B"))
    biblioteca.insertar("c", _cancion("Cancion C"))

    assert biblioteca.buscar("a")["titulo"] == "Cancion A"
    assert biblioteca.buscar("b")["titulo"] == "Cancion B"
    assert biblioteca.buscar("c")["titulo"] == "Cancion C"
    assert len(biblioteca) == 3


def test_todas_las_canciones_devuelve_todo_lo_insertado():
    biblioteca = TablaHash()
    biblioteca.insertar("001", _cancion("A"))
    biblioteca.insertar("002", _cancion("B"))

    titulos = {c["titulo"] for c in biblioteca.todas_las_canciones()}
    assert titulos == {"A", "B"}