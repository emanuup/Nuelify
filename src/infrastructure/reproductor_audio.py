"""
Reproductor de audio: envuelve pygame.mixer para que el resto del
programa no dependa directamente de esa librería.

Si mañana quisieras cambiar pygame por otra librería de audio, solo
tendrías que reescribir este archivo, sin tocar la interfaz ni los
gestores.
"""

import pygame


class ReproductorAudio:
    def __init__(self):
        pygame.mixer.init()
        self.ruta_actual = None
        self.en_pausa = False

    def reproducir(self, ruta_archivo):
        """Carga y empieza a reproducir un archivo de audio desde el inicio."""
        pygame.mixer.music.load(ruta_archivo)
        pygame.mixer.music.play()
        self.ruta_actual = ruta_archivo
        self.en_pausa = False

    def pausar(self):
        pygame.mixer.music.pause()
        self.en_pausa = True

    def reanudar(self):
        pygame.mixer.music.unpause()
        self.en_pausa = False

    def alternar_pausa(self):
        """Pausa si está sonando, reanuda si está en pausa."""
        if self.en_pausa:
            self.reanudar()
        else:
            self.pausar()
        return self.en_pausa

    def detener(self):
        pygame.mixer.music.stop()
        self.ruta_actual = None
        self.en_pausa = False

    def esta_sonando(self):
        """True si hay audio reproduciéndose en este momento."""
        return pygame.mixer.music.get_busy()

    def ajustar_volumen(self, valor):
        """Volumen entre 0.0 (silencio) y 1.0 (máximo)."""
        pygame.mixer.music.set_volume(max(0.0, min(1.0, valor)))

    def posicion_segundos(self):
        """
        Segundos transcurridos de la canción actual.
        pygame devuelve milisegundos, y -1 si no hay nada sonando.
        """
        ms = pygame.mixer.music.get_pos()
        return ms / 1000 if ms > 0 else 0