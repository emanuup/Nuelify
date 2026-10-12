"""
Lector de archivos de música: escanea una carpeta y extrae los metadatos
(título, artista, álbum, duración) de cada canción usando mutagen.
"""

import os
from mutagen import File as ArchivoAudio

EXTENSIONES_VALIDAS = {".mp3", ".wav", ".flac", ".ogg", ".m4a"}


def es_archivo_de_musica(nombre_archivo):
    """Revisa si la extensión del archivo es una de las que soportamos."""
    _, extension = os.path.splitext(nombre_archivo)
    return extension.lower() in EXTENSIONES_VALIDAS


def leer_metadatos(ruta_archivo):
    """
    Lee un archivo de música y devuelve un diccionario con sus metadatos.
    Si el archivo no tiene algún dato (por ejemplo, no tiene tag de artista),
    usa un valor por defecto en vez de fallar.
    """
    audio = ArchivoAudio(ruta_archivo, easy=True)

    if audio is None:
        return None  # mutagen no reconoció el archivo como audio válido

    nombre_sin_extension = os.path.splitext(os.path.basename(ruta_archivo))[0]
    titulo = _primer_valor(audio, "title") or nombre_sin_extension
    artista = _primer_valor(audio, "artist") or "Artista desconocido"
    album = _primer_valor(audio, "album") or "Álbum desconocido"
    duracion = round(audio.info.length) if audio.info else 0  # en segundos

    return {
        "titulo": titulo,
        "artista": artista,
        "album": album,
        "duracion": duracion,
        "ruta": ruta_archivo,
    }


def _primer_valor(audio, clave):
    """mutagen guarda cada tag como una lista (puede haber más de un artista, etc.)."""
    valores = audio.get(clave)
    return valores[0] if valores else None


def escanear_carpeta(ruta_carpeta):
    """
    Recorre una carpeta y devuelve los metadatos de todas las canciones
    que encuentre en ella. No entra en subcarpetas.
    """
    canciones = []
    for nombre in sorted(os.listdir(ruta_carpeta)):
        if not es_archivo_de_musica(nombre):
            continue
        ruta_completa = os.path.join(ruta_carpeta, nombre)
        metadatos = leer_metadatos(ruta_completa)
        if metadatos:
            canciones.append(metadatos)
    return canciones


if __name__ == "__main__":
    import sys

    carpeta = sys.argv[1] if len(sys.argv) > 1 else "data"
    canciones = escanear_carpeta(carpeta)

    print(f"Se encontraron {len(canciones)} canciones en '{carpeta}':")
    for c in canciones:
        minutos, segundos = divmod(c["duracion"], 60)
        print(f"  {c['titulo']} - {c['artista']} ({minutos}:{segundos:02d})")