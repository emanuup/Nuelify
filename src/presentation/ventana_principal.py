"""
Ventana principal del launcher de música.

Estética: terminal minimalista — fondo casi negro neutro, un único color
de acento en cobre apagado, tipografía monoespaciada y espaciado amplio.
"""

import tkinter as tk
from tkinter import filedialog

from application.gestor_biblioteca import GestorBiblioteca
from application.gestor_reproduccion import GestorReproduccion
from infrastructure.reproductor_audio import ReproductorAudio

# ---------------------------------------------------------------------------
# Paleta y tipografía: todo centralizado aquí para cambiar el look en un lugar
# ---------------------------------------------------------------------------
FONDO = "#0e0e10"           # fondo general, negro neutro
SUPERFICIE = "#151517"      # paneles ligeramente elevados
BORDE = "#242428"           # líneas divisorias sutiles
TEXTO = "#e4e4e7"           # texto principal
TEXTO_TENUE = "#6b6b75"     # texto secundario, metadatos
ACENTO = "#b8865b"          # cobre apagado: un solo acento en toda la app
ACENTO_TENUE = "#6d523a"    # versión apagada del acento

FUENTE = "JetBrains Mono"   # si no está instalada, Tk usa una monoespaciada del sistema
FUENTE_RESPALDO = "monospace"


class VentanaPrincipal:
    def __init__(self, raiz):
        self.raiz = raiz
        self.biblioteca = GestorBiblioteca()
        self.reproduccion = GestorReproduccion()
        self.audio = ReproductorAudio()
        self.canciones_visibles = []

        self._configurar_ventana()
        self._construir_interfaz()
        self._cargar_biblioteca_guardada()

    # -- Configuración general -------------------------------------------------

    def _configurar_ventana(self):
        self.raiz.title("nuelify")
        self.raiz.geometry("900x600")
        self.raiz.minsize(700, 450)
        self.raiz.configure(bg=FONDO)

    def _fuente(self, tamano=11, peso="normal"):
        """Usa JetBrains Mono si existe; si no, cualquier monoespaciada."""
        familias = self.raiz.tk.call("font", "families")
        familia = FUENTE if FUENTE in familias else FUENTE_RESPALDO
        return (familia, tamano, peso)

    # -- Construcción de la interfaz -------------------------------------------

    def _construir_interfaz(self):
        self._construir_encabezado()
        self._construir_busqueda()
        self._construir_lista()
        self._construir_barra_inferior()

    def _construir_encabezado(self):
        encabezado = tk.Frame(self.raiz, bg=FONDO)
        encabezado.pack(fill="x", padx=32, pady=(28, 0))

        tk.Label(
            encabezado, text="nuelify", bg=FONDO, fg=TEXTO,
            font=self._fuente(17, "bold"),
        ).pack(side="left")

        tk.Label(
            encabezado, text="// reproductor local", bg=FONDO, fg=TEXTO_TENUE,
            font=self._fuente(10),
        ).pack(side="left", padx=(12, 0), pady=(5, 0))

        self.boton_carpeta = tk.Button(
            encabezado, text="+ abrir carpeta", command=self._elegir_carpeta,
            bg=FONDO, fg=ACENTO, activebackground=SUPERFICIE, activeforeground=ACENTO,
            font=self._fuente(10), relief="flat", bd=0, cursor="hand2",
            highlightthickness=0, padx=10, pady=4,
        )
        self.boton_carpeta.pack(side="right")

    def _construir_busqueda(self):
        contenedor = tk.Frame(self.raiz, bg=FONDO)
        contenedor.pack(fill="x", padx=32, pady=(24, 0))

        tk.Label(
            contenedor, text="/", bg=FONDO, fg=ACENTO_TENUE,
            font=self._fuente(12),
        ).pack(side="left", padx=(0, 10))

        self.entrada_busqueda = tk.Entry(
            contenedor, bg=FONDO, fg=TEXTO, insertbackground=ACENTO,
            font=self._fuente(11), relief="flat", bd=0, highlightthickness=0,
        )
        self.entrada_busqueda.pack(side="left", fill="x", expand=True, ipady=6)
        # Cada tecla que se suelta dispara el filtrado: búsqueda en vivo
        self.entrada_busqueda.bind("<KeyRelease>", self._filtrar)

        tk.Frame(self.raiz, bg=BORDE, height=1).pack(fill="x", padx=32, pady=(0, 4))

    def _construir_lista(self):
        contenedor = tk.Frame(self.raiz, bg=FONDO)
        contenedor.pack(fill="both", expand=True, padx=32, pady=(16, 0))

        self.lista = tk.Listbox(
            contenedor, bg=FONDO, fg=TEXTO, font=self._fuente(11),
            selectbackground=SUPERFICIE, selectforeground=ACENTO,
            relief="flat", bd=0, highlightthickness=0, activestyle="none",
        )
        self.lista.pack(side="left", fill="both", expand=True)
        # Doble clic sobre una canción la reproduce
        self.lista.bind("<Double-Button-1>", self._reproducir_seleccion)

        barra = tk.Scrollbar(
            contenedor, command=self.lista.yview, bg=FONDO,
            troughcolor=FONDO, bd=0, relief="flat", width=8,
            activebackground=ACENTO_TENUE,
        )
        barra.pack(side="right", fill="y")
        self.lista.config(yscrollcommand=barra.set)

    def _construir_barra_inferior(self):
        tk.Frame(self.raiz, bg=BORDE, height=1).pack(fill="x", padx=32, pady=(16, 0))

        barra = tk.Frame(self.raiz, bg=FONDO)
        barra.pack(fill="x", padx=32, pady=(18, 28))

        # Panel izquierdo: qué está sonando
        info = tk.Frame(barra, bg=FONDO)
        info.pack(side="left", fill="x", expand=True)

        self.etiqueta_titulo = tk.Label(
            info, text="nada en reproducción", bg=FONDO, fg=TEXTO,
            font=self._fuente(11), anchor="w",
        )
        self.etiqueta_titulo.pack(fill="x")

        self.etiqueta_artista = tk.Label(
            info, text="—", bg=FONDO, fg=TEXTO_TENUE,
            font=self._fuente(9), anchor="w",
        )
        self.etiqueta_artista.pack(fill="x", pady=(3, 0))

        # Panel derecho: controles de transporte
        controles = tk.Frame(barra, bg=FONDO)
        controles.pack(side="right")

        self._boton_control(controles, "|<", self._anterior)
        self.boton_play = self._boton_control(controles, "||", self._alternar_pausa)
        self._boton_control(controles, ">|", self._siguiente)

    def _boton_control(self, padre, texto, comando):
        boton = tk.Button(
            padre, text=texto, command=comando,
            bg=FONDO, fg=TEXTO, activebackground=FONDO, activeforeground=ACENTO,
            font=self._fuente(12), relief="flat", bd=0, cursor="hand2",
            highlightthickness=0, padx=12, pady=2, width=3,
        )
        boton.pack(side="left", padx=4)
        return boton

    # -- Acciones --------------------------------------------------------------

    def _cargar_biblioteca_guardada(self):
        total = self.biblioteca.cargar()
        if total:
            self._refrescar_lista(self.biblioteca.todas())

    def _elegir_carpeta(self):
        carpeta = filedialog.askdirectory(title="Elige una carpeta con música")
        if not carpeta:
            return
        self.biblioteca.cargar_desde_carpeta(carpeta)
        self.biblioteca.guardar()
        self._refrescar_lista(self.biblioteca.todas())

    def _filtrar(self, evento=None):
        texto = self.entrada_busqueda.get().strip()
        encontradas = self.biblioteca.buscar_por_titulo(texto) if texto else self.biblioteca.todas()
        self._refrescar_lista(encontradas)

    def _refrescar_lista(self, canciones):
        self.canciones_visibles = canciones
        self.lista.delete(0, tk.END)
        for cancion in canciones:
            minutos, segundos = divmod(cancion.get("duracion", 0), 60)
            linea = f"  {cancion['titulo']:<42.42}  {cancion['artista']:<24.24}  {minutos}:{segundos:02d}"
            self.lista.insert(tk.END, linea)

    def _reproducir_seleccion(self, evento=None):
        seleccion = self.lista.curselection()
        if not seleccion:
            return
        cancion = self.canciones_visibles[seleccion[0]]
        self.reproduccion.cargar_playlist(self.canciones_visibles)
        # Deja la playlist posicionada en la canción elegida
        for _ in range(seleccion[0]):
            self.reproduccion.playlist_actual.siguiente_cancion()
        self._reproducir(cancion)

    def _reproducir(self, cancion):
        if cancion is None:
            return
        self.reproduccion.reproducir(cancion)
        self.audio.reproducir(cancion["ruta"])
        self.boton_play.config(text="||")
        self.etiqueta_titulo.config(text=cancion["titulo"], fg=ACENTO)
        self.etiqueta_artista.config(text=cancion["artista"])

    def _alternar_pausa(self):
        if self.reproduccion.reproduciendo_ahora is None:
            return
        en_pausa = self.audio.alternar_pausa()
        self.boton_play.config(text=">" if en_pausa else "||")

    def _siguiente(self):
        self._reproducir(self.reproduccion.siguiente())

    def _anterior(self):
        cancion = self.reproduccion.anterior()
        if cancion:
            self.reproduccion.reproduciendo_ahora = cancion
            self.audio.reproducir(cancion["ruta"])
            self.etiqueta_titulo.config(text=cancion["titulo"], fg=ACENTO)
            self.etiqueta_artista.config(text=cancion["artista"])


def iniciar():
    raiz = tk.Tk()
    VentanaPrincipal(raiz)
    raiz.mainloop()


if __name__ == "__main__":
    iniciar()