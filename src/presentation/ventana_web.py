"""
Ventana web del launcher.

La interfaz es HTML/CSS/JS (carpeta web/). Python sigue haciendo el trabajo
de verdad: biblioteca, cola, historial y audio. La clase Api es el puente:
el JavaScript llama a sus métodos públicos (los que no empiezan con "_").

Para cambiar el look solo se tocan los archivos de web/. La lógica no cambia.
"""

import base64
import functools
import sys
import threading
from pathlib import Path

import webview
from mutagen import File

from application.gestor_biblioteca import GestorBiblioteca
from application.gestor_reproduccion import GestorReproduccion
from infrastructure.reproductor_audio import ReproductorAudio

def _carpeta_web():
    # Dentro del ejecutable, PyInstaller descomprime todo en sys._MEIPASS
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "presentation" / "web"
    return Path(__file__).resolve().parent / "web"


RUTA_WEB = _carpeta_web()

# True = sin la barra del sistema: solo se ve el reproductor, como en la
# referencia. La franja del título del HTML sirve para arrastrar la ventana.
SIN_MARCO = True

# Tamaño del reproductor solo (sin la biblioteca abierta). El alto es una
# estimación: al abrir, el JS mide el real y la ventana se corrige sola.
ANCHO_VENTANA = 640
ALTO_VENTANA = 400

VOLUMEN_INICIAL = 70  # porcentaje

EXTENSIONES_IMAGEN = {".jpg", ".jpeg", ".png"}
NOMBRES_CARATULA = {
    "cover", "folder", "front", "album", "albumart", "artwork",
    "caratula", "portada",
}


# ---------------------------------------------------------------------------
# Carátulas: primero la que viene dentro del archivo, si no, una imagen
# suelta (cover.jpg, folder.jpg...) en la misma carpeta.
# ---------------------------------------------------------------------------

def _caratula_incrustada(ruta):
    try:
        audio = File(ruta)
    except Exception:
        return None
    if audio is None:
        return None
    if getattr(audio, "pictures", None):              # FLAC
        return audio.pictures[0].data
    tags = audio.tags
    if tags is None:
        return None
    if hasattr(tags, "getall"):                        # MP3
        fotos = tags.getall("APIC")
        if fotos:
            return fotos[0].data
    if "covr" in tags:                                 # M4A
        return bytes(tags["covr"][0])
    return None


def _caratula_en_carpeta(ruta):
    try:
        for archivo in Path(ruta).parent.iterdir():
            if (archivo.suffix.lower() in EXTENSIONES_IMAGEN
                    and archivo.stem.lower() in NOMBRES_CARATULA):
                return archivo.read_bytes()
    except OSError:
        pass
    return None


def _a_data_uri(datos):
    es_png = datos[:8] == b"\x89PNG\r\n\x1a\n"
    mime = "image/png" if es_png else "image/jpeg"
    return f"data:{mime};base64," + base64.b64encode(datos).decode("ascii")


def _tipo_dialogo_carpeta():
    # pywebview nuevo usa FileDialog.FOLDER; el viejo, FOLDER_DIALOG
    if hasattr(webview, "FileDialog"):
        return webview.FileDialog.FOLDER
    return webview.FOLDER_DIALOG


def _con_cerrojo(metodo):
    """JS llama a la Api desde varios hilos a la vez (el reloj y los clics).
    El cerrojo hace que solo uno toque los gestores al mismo tiempo."""
    @functools.wraps(metodo)
    def envoltura(self, *args, **kwargs):
        with self._cerrojo:
            return metodo(self, *args, **kwargs)
    return envoltura


# ---------------------------------------------------------------------------
# Api: lo que el JavaScript puede pedirle a Python
# ---------------------------------------------------------------------------

class Api:
    def __init__(self):
        # Lo que empieza con "_" no se expone a JS
        self._cerrojo = threading.RLock()
        self._biblioteca = GestorBiblioteca()
        self._reproduccion = GestorReproduccion()
        self._audio = ReproductorAudio()

        self._volumen = VOLUMEN_INICIAL / 100
        self._audio.ajustar_volumen(self._volumen)

        self._total = self._biblioteca.cargar() or 0
        self._visibles = self._biblioteca.todas()

    # -- Biblioteca ---------------------------------------------------------

    @_con_cerrojo
    def listar(self, texto=""):
        texto = (texto or "").strip()
        if texto:
            self._visibles = self._biblioteca.buscar_por_titulo(texto)
        else:
            self._visibles = self._biblioteca.todas()
        return [
            {
                "titulo": c.get("titulo", "Sin título"),
                "artista": c.get("artista", "Artista desconocido"),
                "duracion": c.get("duracion", 0),
                "ruta": str(c.get("ruta", "")),
            }
            for c in self._visibles
        ]

    def elegir_carpeta(self):
        # El diálogo va fuera del cerrojo: así el reloj sigue funcionando
        resultado = webview.windows[0].create_file_dialog(_tipo_dialogo_carpeta())
        if not resultado:
            return None
        with self._cerrojo:
            self._biblioteca.cargar_desde_carpeta(resultado[0])
            self._biblioteca.guardar()
            self._visibles = self._biblioteca.todas()
            self._total = len(self._visibles)
            return self._total

    # -- Reproducción -------------------------------------------------------

    @_con_cerrojo
    def reproducir(self, indice):
        if not 0 <= indice < len(self._visibles):
            return False
        cancion = self._visibles[indice]
        self._reproduccion.cargar_playlist(self._visibles)
        # Deja la playlist parada en la canción elegida
        for _ in range(indice):
            self._reproduccion.playlist_actual.siguiente_cancion()
        self._reproduccion.reproducir(cancion)
        return self._sonar(cancion)

    @_con_cerrojo
    def reanudar(self):
        """Botón ▶: sigue si estaba en pausa; si no hay nada, empieza la lista."""
        if self._audio.en_pausa:
            self._audio.reanudar()
        elif self._reproduccion.reproduciendo_ahora is None and self._visibles:
            self.reproducir(0)

    @_con_cerrojo
    def pausar(self):
        if self._reproduccion.reproduciendo_ahora is not None and not self._audio.en_pausa:
            self._audio.pausar()

    @_con_cerrojo
    def detener(self):
        self._parar()

    @_con_cerrojo
    def siguiente(self):
        cancion = self._reproduccion.siguiente()   # ya guarda el historial
        if cancion is not None:
            self._sonar(cancion)

    @_con_cerrojo
    def anterior(self):
        cancion = self._reproduccion.anterior()
        if cancion is not None:
            self._sonar(cancion)

    @_con_cerrojo
    def ir_a(self, fraccion):
        """Salta a un punto de la canción. fraccion va de 0.0 (inicio) a 1.0 (final)."""
        actual = self._reproduccion.reproduciendo_ahora
        if actual is None:
            return False
        duracion = actual.get("duracion", 0)
        if duracion <= 0:
            return False
        fraccion = max(0.0, min(1.0, fraccion))
        # Un segundo antes del final como máximo: así no salta a la siguiente por error
        segundos = min(fraccion * duracion, max(0, duracion - 1))
        return self._audio.ir_a(segundos)

    @_con_cerrojo
    def ajustar_volumen(self, porcentaje):
        self._volumen = max(0, min(100, porcentaje)) / 100
        self._audio.ajustar_volumen(self._volumen)

    # -- Lo que la interfaz consulta cada medio segundo ---------------------

    @_con_cerrojo
    def estado(self):
        respuesta = {
            "hay_cancion": False,
            "fin": False,
            "total": self._total,
            "volumen": round(self._volumen * 100),
        }
        actual = self._reproduccion.reproduciendo_ahora
        if actual is None:
            return respuesta

        # Si no está en pausa y ya no suena, la canción terminó: sigue la próxima
        if not self._audio.en_pausa and not self._audio.esta_sonando():
            siguiente = self._reproduccion.siguiente()
            if siguiente is not None and self._sonar(siguiente):
                actual = siguiente
            else:
                self._parar()
                respuesta["fin"] = True
                return respuesta

        respuesta.update({
            "hay_cancion": True,
            "titulo": actual.get("titulo", "Sin título"),
            "artista": actual.get("artista", "Artista desconocido"),
            "ruta": str(actual.get("ruta", "")),
            "duracion": actual.get("duracion", 0),
            "transcurrido": self._audio.posicion_segundos(),
            "en_pausa": self._audio.en_pausa,
        })
        return respuesta

    @_con_cerrojo
    def caratula(self):
        actual = self._reproduccion.reproduciendo_ahora
        if actual is None:
            return None
        ruta = actual.get("ruta")
        datos = _caratula_incrustada(ruta) or _caratula_en_carpeta(ruta)
        return _a_data_uri(datos) if datos else None

    def cerrar(self):
        webview.windows[0].destroy()

    def ajustar_ventana(self, ancho, alto):
        """El JS avisa cuánto mide el reproductor (crece al abrir la biblioteca)."""
        try:
            webview.windows[0].resize(int(ancho), int(alto))
        except Exception:
            pass  # algunos escritorios no dejan cambiar el tamaño desde el programa

    # -- Interno ------------------------------------------------------------

    def _sonar(self, cancion):
        try:
            self._audio.reproducir(cancion["ruta"])
            return True
        except Exception:
            self._parar()
            return False

    def _parar(self):
        self._audio.detener()
        self._reproduccion.reproduciendo_ahora = None


def iniciar():
    api = Api()
    webview.create_window(
        "Nuelify",
        str(RUTA_WEB / "index.html"),
        js_api=api,
        width=ANCHO_VENTANA,
        height=ALTO_VENTANA,
        min_size=(320, 200),
        background_color="#bcbcbc",
        frameless=SIN_MARCO,
        easy_drag=False,
    )
    if sys.platform.startswith("linux"):
        # En Linux usamos Qt directo: evita el intento fallido con GTK
        try:
            webview.start(gui="qt")
            return
        except Exception:
            pass
    webview.start()


if __name__ == "__main__":
    iniciar()