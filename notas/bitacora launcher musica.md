# Bitácora — Launcher de música (proyecto de grado)

> Notas técnicas del proceso de construcción, pensadas para consultarlas en futuros proyectos.

## Resumen del proyecto

Aplicación de escritorio en Python que organiza, busca y reproduce música local, construida para demostrar la aplicación práctica de estructuras de datos implementadas manualmente. Corre igual en Linux (desarrollo) y Windows (evaluación del profesor). Interfaz en Tkinter, estética minimalista de terminal (fondo casi negro, acento único en cobre apagado, tipografía monoespaciada).

## Estado del proyecto

| Capa | Contenido | Estado |
|---|---|---|
| Dominio | Lista doblemente enlazada, cola, pila, tabla hash | ✅ Completa (21 tests) |
| Infraestructura | Lector de metadatos (mutagen), persistencia JSON, reproductor de audio (pygame-ce) | ✅ Completa (10 tests) |
| Aplicación | GestorBiblioteca, GestorReproduccion | ✅ Completa (10 tests) |
| Presentación | Ventana principal en Tkinter | ✅ Completa, probada de punta a punta con música real |
| Despliegue | Primer push a GitHub, empaquetado multiplataforma | ⬜ Pendiente |

Total: 41 pruebas automatizadas, todas pasando.

## Decisiones de arquitectura y por qué

- **Arquitectura en capas** (presentación, aplicación, dominio, infraestructura, recursos externos): separa la interfaz de la lógica de negocio y de las estructuras de datos. Facilita explicar el proyecto en la sustentación y facilita las pruebas, porque cada capa se puede probar por separado.
- **Python + Tkinter + pygame-ce**: ambas librerías son multiplataforma sin instalaciones extra (Tkinter viene con la instalación estándar de Python). Esto resolvió directamente el requisito de "funciona igual en Linux y Windows".
- **Estructuras de datos elegidas para que cada una tenga una razón funcional real**, no forzada:

| Estructura | Módulo que representa | Por qué esa estructura |
|---|---|---|
| Lista doblemente enlazada | Playlists | Se necesita navegar adelante/atrás e insertar en cualquier posición |
| Cola (queue, FIFO) | Cola de reproducción | El orden de "lo próximo a sonar" es estrictamente de llegada |
| Pila (stack, LIFO) | Historial / botón "anterior" | Lo último reproducido es lo primero que se recupera |
| Tabla hash | Biblioteca musical completa | Búsqueda por id/nombre en tiempo casi constante, con encadenamiento para colisiones y redimensionamiento automático |
- **La cola tiene prioridad sobre la playlist** en `GestorReproduccion.siguiente()`: si hay algo encolado suena primero, pero la posición en la playlist no se pierde, solo queda en pausa hasta que la cola se vacía. Decisión de diseño consciente, no accidental.

## Conceptos nuevos que aprendí en el camino

**Entorno virtual (venv):** una copia aislada de Python solo para este proyecto, con sus propios paquetes. Evita que las dependencias de un proyecto choquen con las de otro o con el Python del sistema.
- Crear: `python -m venv .venv` — Activar: `source .venv/bin/activate` (se nota porque el prompt empieza con `(.venv)`)

**pytest:** framework para escribir pruebas automáticas. Cada test es una pregunta puntual al código con una respuesta ya conocida. Patrón usado en cada test: preparar datos → ejecutar la operación → verificar con `assert`.
- Correr con `python -m pytest`. Los archivos deben empezar exactamente con `test_` o pytest no los detecta.

**conftest.py:** le dice a pytest dónde buscar los módulos del proyecto. Va en la raíz, agrega `src/` a la ruta de búsqueda.

**.gitignore:** qué no subir al repositorio: el venv, las cachés (`__pycache__/`, `.pytest_cache/`), carpetas de build (`build/`, `dist/`), y la config de Obsidian (`.obsidian/`).

**JSON:** formato de texto para guardar listas y diccionarios de Python en un archivo (llaves y corchetes, básicamente lo mismo que ya se ve en pantalla al imprimir un dict). Se usa para persistir la biblioteca y las playlists entre sesiones.

**mutagen:** librería para leer metadatos (título, artista, duración) directo de un archivo de audio, sin tener que abrirlo manualmente.

**Tkinter:** librería de interfaz gráfica incluida con Python. Funciona con *widgets* organizados en contenedores, y es dirigida por eventos — se registran funciones que Tkinter ejecuta cuando el usuario hace algo (clic, tecla), en vez de un flujo secuencial. `mainloop()` es el bucle que mantiene la ventana abierta.

**pygame-ce:** módulo de audio (fork de pygame). Se usa `pygame.mixer` para reproducir sonido, algo que Tkinter no sabe hacer por sí solo.

**Herramientas de diseño (Figma/Whimsical/Canva) vs. código:** producen una imagen/mockup de cómo se ve la interfaz, no código que se "inserte" en la app. Para Tkinter, el diseño se traduce a mano (colores, posiciones, tipografía) a las constantes y widgets de Python. El botón "exportar código" de Figma genera CSS/React, que no sirve para una app de escritorio en Tkinter.

## Problemas que me encontré y cómo se resolvieron

- **`zsh: command not found: pip`** → el sistema no tenía `pip` global. Se resolvió creando un venv (`python -m venv .venv`), que trae su propio `pip`.
- **`source .venv/bin/activate` decía que no existía el archivo** → el venv nunca se había terminado de crear. Se resolvió creándolo directo por comando en la terminal.
- **pytest "collected 9 items" en vez de 13** → un archivo de prueba tenía un typo en el nombre (`tets_` en vez de `test_`). pytest solo reconoce archivos que empiezan exactamente con `test_`.
- **Obsidian no mostraba la carpeta `notas`** → al crear la bóveda se eligió "crear nueva bóveda", lo que generó una carpeta separada y vacía en vez de abrir el proyecto existente. Se resolvió con "abrir carpeta como bóveda", apuntando directo a la raíz del proyecto.
- **`pygame.mixer` no existía (`ModuleNotFoundError`)** → el paquete oficial `pygame` no tenía el módulo `mixer` compilado para Python 3.14 todavía. Se resolvió cambiando a `pygame-ce`, un reemplazo directo (mismo `import pygame`) con soporte oficial para esa versión de Python.

## Checklist reutilizable para arrancar un proyecto de Python desde cero

1. Definir la arquitectura (capas u otro patrón) antes de escribir código.
2. Crear la estructura de carpetas siguiendo esa arquitectura.
3. `python -m venv .venv` y activarlo.
4. Crear `.gitignore` (venv, cachés, carpetas de build, config de Obsidian) antes del primer commit.
5. `pip install pytest` y crear `conftest.py` en la raíz apuntando a `src/`.
6. Escribir cada módulo junto con sus pruebas, no todo el código primero y las pruebas al final.
7. `git init`, primer commit, conectar el repositorio remoto, push.
8. Documentar decisiones y problemas en una bitácora como esta, a medida que van apareciendo — no de memoria al final.

## Próximos pasos

- [ ] Primer push a GitHub
- [ ] Empaquetado multiplataforma (PyInstaller + GitHub Actions para generar el `.exe` de Windows)