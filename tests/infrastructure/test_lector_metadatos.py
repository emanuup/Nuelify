"""
Pruebas para el lector de metadatos.
Ejecutar con: pytest

Usamos archivos .wav generados al vuelo (silenciosos, sin contenido real)
para tener algo genuino que mutagen pueda leer, sin depender de canciones
de verdad guardadas en el repositorio.
"""
import tempfile
import wave

from infrastructure.lector_metadatos import escanear_carpeta, es_archivo_de_musica, leer_metadatos


def _crear_wav_de_prueba(ruta, duracion_segundos=2):
    tasa_muestreo = 8000
    with wave.open(str(ruta), "w") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(tasa_muestreo)
        wav.writeframes(b"\x00\x00" * tasa_muestreo * duracion_segundos)


def test_reconoce_extensiones_validas():
    assert es_archivo_de_musica("cancion.mp3")
    assert es_archivo_de_musica("cancion.WAV")  # no debe importar mayúsculas/minúsculas
    assert not es_archivo_de_musica("portada.jpg")
    assert not es_archivo_de_musica("notas.txt")


def test_leer_metadatos_de_un_wav_sin_tags(tmp_path):
    ruta = tmp_path / "mi_cancion.wav"
    _crear_wav_de_prueba(ruta, duracion_segundos=3)

    metadatos = leer_metadatos(str(ruta))

    assert metadatos is not None
    assert metadatos["titulo"] == "mi_cancion"  # usa el nombre del archivo si no hay tag
    assert metadatos["artista"] == "Artista desconocido"
    assert metadatos["duracion"] == 3
    assert metadatos["ruta"] == str(ruta)


def test_escanear_carpeta_encuentra_solo_archivos_de_musica(tmp_path):
    _crear_wav_de_prueba(tmp_path / "cancion1.wav", duracion_segundos=1)
    _crear_wav_de_prueba(tmp_path / "cancion2.wav", duracion_segundos=1)
    (tmp_path / "notas.txt").write_text("esto no es música")

    canciones = escanear_carpeta(str(tmp_path))

    assert len(canciones) == 2
    titulos = {c["titulo"] for c in canciones}
    assert titulos == {"cancion1", "cancion2"}


def test_escanear_carpeta_vacia_no_encuentra_nada():
    with tempfile.TemporaryDirectory() as carpeta_vacia:
        assert escanear_carpeta(carpeta_vacia) == []