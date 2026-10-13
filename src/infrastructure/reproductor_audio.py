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
        # pygame.get_pos() cuenta desde el último play(), no desde el inicio
        # de la canción. Si saltamos a los 90 s, guardamos ese 90 aquí.
        self._desfase = 0.0

    def reproducir(self, ruta_archivo):
        """Carga y empieza a reproducir un archivo de audio desde el inicio."""
        pygame.mixer.music.load(ruta_archivo)
        pygame.mixer.music.play()
        self.ruta_actual = ruta_archivo
        self.en_pausa = False
        self._desfase = 0.0

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
        self._desfase = 0.0

    def esta_sonando(self):
        """True si hay audio reproduciéndose en este momento."""
        return pygame.mixer.music.get_busy()

    def ajustar_volumen(self, valor):
        """Volumen entre 0.0 (silencio) y 1.0 (máximo)."""
        pygame.mixer.music.set_volume(max(0.0, min(1.0, valor)))

    def ir_a(self, segundos):
        """
        Salta a un punto de la canción actual (en segundos).
        Devuelve True si pudo. Con algunos formatos (por ejemplo WAV)
        pygame no deja saltar: ahí devuelve False y no toca nada.
        """
        if self.ruta_actual is None:
            return False
        segundos = max(0.0, segundos)
        try:
            # play() siempre reanuda, aunque estuviera en pausa
            pygame.mixer.music.play(start=segundos)
        except (NotImplementedError, pygame.error):
            return False
        self._desfase = segundos
        if self.en_pausa:
            pygame.mixer.music.pause()   # respeta la pausa del usuario
        return True

    def posicion_segundos(self):
        """
        Segundos transcurridos de la canción actual, contando desde el inicio
        de la canción (incluye los saltos hechos con ir_a).
        pygame devuelve milisegundos, y -1 si no hay nada sonando.
        """
        if self.ruta_actual is None:
            return 0.0
        ms = pygame.mixer.music.get_pos()
        return self._desfase + (ms / 1000 if ms > 0 else 0)