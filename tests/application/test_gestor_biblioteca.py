"""
Pruebas para el gestor de biblioteca.
Ejecutar con: pytest
"""
import wave

from application.gestor_biblioteca import GestorBiblioteca


def _crear_wav_de_prueba(ruta, duracion_segundos=1):
    tasa_muestreo = 8000
    with wave.open(str(ruta), "w") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(tasa_muestreo)
        wav.writeframes(b"\x00\x00" * tasa_muestreo * duracion_segundos)


def test_cargar_desde_carpeta_indexa_las_canciones(tmp_path):
    _crear_wav_de_prueba(tmp_path / "cancion1.wav")
    _crear_wav_de_prueba(tmp_path / "cancion2.wav")

    gestor = GestorBiblioteca()
    total = gestor.cargar_desde_carpeta(str(tmp_path))

    assert total == 2
    assert len(gestor.todas()) == 2


def test_buscar_por_titulo_encuentra_coincidencias_parciales(tmp_path):
    _crear_wav_de_prueba(tmp_path / "bohemian_rhapsody.wav")
    _crear_wav_de_prueba(tmp_path / "otra_cancion.wav")

    gestor = GestorBiblioteca()
    gestor.cargar_desde_carpeta(str(tmp_path))

    resultados = gestor.buscar_por_titulo("bohemian")
    assert len(resultados) == 1
    assert resultados[0]["titulo"] == "bohemian_rhapsody"


def test_buscar_por_titulo_no_distingue_mayusculas(tmp_path):
    _crear_wav_de_prueba(tmp_path / "Bohemian_Rhapsody.wav")

    gestor = GestorBiblioteca()
    gestor.cargar_desde_carpeta(str(tmp_path))

    assert len(gestor.buscar_por_titulo("BOHEMIAN")) == 1


def test_guardar_y_cargar_restaura_la_biblioteca(tmp_path):
    ruta_musica = tmp_path / "musica"
    ruta_musica.mkdir()
    _crear_wav_de_prueba(ruta_musica / "cancion1.wav")

    ruta_guardado = tmp_path / "biblioteca.json"

    gestor1 = GestorBiblioteca()
    gestor1.cargar_desde_carpeta(str(ruta_musica))
    gestor1.guardar(str(ruta_guardado))

    gestor2 = GestorBiblioteca()
    total_restaurado = gestor2.cargar(str(ruta_guardado))

    assert total_restaurado == 1
    assert len(gestor2.todas()) == 1