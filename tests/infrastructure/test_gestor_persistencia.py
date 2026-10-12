"""
Pruebas para el gestor de persistencia.
Ejecutar con: pytest
"""
import json

from infrastructure.gestor_persistencia import cargar, guardar


def test_guardar_y_cargar_devuelve_los_mismos_datos(tmp_path):
    ruta = tmp_path / "biblioteca.json"
    datos = [{"titulo": "A", "artista": "X"}, {"titulo": "B", "artista": "Y"}]

    guardar(datos, str(ruta))
    resultado = cargar(str(ruta))

    assert resultado == datos


def test_cargar_archivo_que_no_existe_devuelve_valor_por_defecto():
    resultado = cargar("no/existe/este/archivo.json", valor_por_defecto=[])
    assert resultado == []


def test_cargar_sin_valor_por_defecto_devuelve_none():
    assert cargar("no/existe/este/archivo.json") is None


def test_guardar_crea_la_carpeta_si_no_existe(tmp_path):
    ruta = tmp_path / "subcarpeta" / "biblioteca.json"
    guardar([{"titulo": "A"}], str(ruta))

    assert ruta.exists()


def test_cargar_archivo_json_corrupto_devuelve_valor_por_defecto(tmp_path):
    ruta = tmp_path / "corrupto.json"
    ruta.write_text("esto no es json válido {{{")

    resultado = cargar(str(ruta), valor_por_defecto="respaldo")
    assert resultado == "respaldo"


def test_el_archivo_guardado_es_json_legible_por_fuera(tmp_path):
    ruta = tmp_path / "biblioteca.json"
    guardar([{"titulo": "Ñandú", "artista": "Test"}], str(ruta))

    # Verifica directamente con la librería json, sin pasar por nuestra función,
    # para confirmar que el archivo es JSON válido y bien formado.
    with open(ruta, encoding="utf-8") as f:
        contenido = json.load(f)
    assert contenido[0]["titulo"] == "Ñandú"