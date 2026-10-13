"use strict";

/* ==========================================================================
   Nuelify · interfaz web
   JS solo dibuja y manda clics. La lógica real vive en Python (ventana_web.py).
   ========================================================================== */

const $ = (id) => document.getElementById(id);

let api = null;            // puente hacia Python, se llena cuando pywebview está listo
let rutaActual = null;     // canción que se está mostrando (para cambiar la carátula)
let avisoTexto = "";
let avisoHasta = 0;

/* ---------- Escala: el diseño mide 640px y se encoge si la ventana es angosta ---------- */

const ANCHO_DISENO = 640;

let altoPedido = 0;

function ajustarEscala() {
  const alto = $("lienzo").offsetHeight;
  // Nunca crece: solo se encoge si la ventana es más chica que el diseño
  const escala = Math.min(1, window.innerWidth / ANCHO_DISENO, window.innerHeight / alto);
  document.documentElement.style.setProperty("--escala", escala);
  // El lienzo se encoge con transform, pero su espacio en la página no:
  // por eso la caja toma la altura ya encogida.
  $("caja").style.height = `${alto * escala}px`;
}

/** Le pide a Python que la ventana mida justo lo que mide el reproductor. */
function ajustarVentana() {
  const alto = $("lienzo").offsetHeight;
  if (!api || alto === altoPedido) return;
  altoPedido = alto;
  api.ajustar_ventana(ANCHO_DISENO, alto);
}

window.addEventListener("resize", ajustarEscala);
new ResizeObserver(() => {      // cambia el alto, por ejemplo al abrir la biblioteca
  ajustarEscala();
  ajustarVentana();
}).observe($("lienzo"));
ajustarEscala();

/* ---------- Utilidades ---------- */

function formatear(segundos) {
  const total = Math.max(0, Math.floor(segundos || 0));
  const minutos = Math.floor(total / 60);
  return `${minutos}:${String(total % 60).padStart(2, "0")}`;
}

/** "1 canción", "2 canciones" */
function contar(n) {
  return `${n} ${n === 1 ? "canción" : "canciones"}`;
}

/** Mensaje temporal en la barra de estado. */
function avisar(texto, milisegundos = 3000) {
  avisoTexto = texto;
  avisoHasta = performance.now() + milisegundos;
}

/**
 * Prepara una barra (volumen o progreso). Devuelve la función que la pinta.
 * Si recibe alCambiar, la barra se puede arrastrar con el mouse.
 */
function crearBarra(barra, alCambiar) {
  const pintar = (fraccion) => {
    barra.style.setProperty("--v", `${Math.round(fraccion * 1000) / 10}%`);
  };
  if (!alCambiar) return pintar;

  barra.classList.add("ajustable");
  let arrastrando = false;

  const fraccionDe = (evento) => {
    const caja = barra.getBoundingClientRect();
    return Math.min(1, Math.max(0, (evento.clientX - caja.left) / caja.width));
  };

  barra.addEventListener("pointerdown", (e) => {
    arrastrando = true;
    barra.dataset.arrastrando = "1";   // el reloj no la repinta mientras la mueves
    barra.setPointerCapture(e.pointerId);
    const f = fraccionDe(e);
    pintar(f);
    alCambiar(f, false);
  });
  barra.addEventListener("pointermove", (e) => {
    if (!arrastrando) return;
    const f = fraccionDe(e);
    pintar(f);
    alCambiar(f, false);
  });
  barra.addEventListener("pointerup", (e) => {
    if (!arrastrando) return;
    arrastrando = false;
    delete barra.dataset.arrastrando;
    alCambiar(fraccionDe(e), true);
  });
  barra.addEventListener("pointercancel", () => {
    arrastrando = false;
    delete barra.dataset.arrastrando;
  });
  return pintar;
}

let duracionActual = 0;   // segundos de la canción que suena (0 si no hay)

/** Barra de progreso: al arrastrar muestra el tiempo destino; al soltar, salta. */
function alCambiarProgreso(fraccion, definitivo) {
  if (!api || duracionActual <= 0) return;
  $("tiempo").textContent = `${formatear(fraccion * duracionActual)} / ${formatear(duracionActual)}`;
  if (!definitivo) return;
  api.ir_a(fraccion).then((ok) => {
    if (!ok) avisar("Este archivo no permite saltar");
    return refrescar();
  });
}

const pintarVolumen = crearBarra($("volumen"), enviarVolumen);
const pintarProgreso = crearBarra($("progreso"), alCambiarProgreso);

/* ---------- Volumen ---------- */

let ultimoEnvio = 0;

function enviarVolumen(fraccion, definitivo) {
  if (!api) return;
  const ahora = performance.now();
  // Mientras se arrastra mandamos como mucho uno cada 60 ms; al soltar, el final
  if (definitivo || ahora - ultimoEnvio > 60) {
    ultimoEnvio = ahora;
    api.ajustar_volumen(Math.round(fraccion * 100));
  }
}

/* ---------- Carátula ---------- */

function mostrarCaratula(uri) {
  const imagen = $("img-caratula");
  const vacia = $("caratula-vacia");
  if (uri) {
    imagen.src = uri;
    imagen.hidden = false;
    vacia.hidden = true;
  } else {
    imagen.hidden = true;
    imagen.removeAttribute("src");
    vacia.hidden = false;
  }
}

/* ---------- Biblioteca ---------- */

function crearCelda(texto, clase) {
  const celda = document.createElement("span");
  celda.textContent = texto;   // textContent: los títulos nunca se interpretan como HTML
  if (clase) celda.className = clase;
  return celda;
}

async function cargarLista() {
  const texto = $("buscar").value;
  const canciones = await api.listar(texto);
  const lista = $("canciones");
  lista.replaceChildren();

  if (canciones.length === 0) {
    const vacio = document.createElement("li");
    vacio.className = "vacio";
    vacio.textContent = texto
      ? "Ninguna canción coincide."
      : "No hay canciones. Pulsa Navegar y elige una carpeta.";
    lista.append(vacio);
    return;
  }

  canciones.forEach((cancion, indice) => {
    const fila = document.createElement("li");
    fila.dataset.ruta = cancion.ruta;
    fila.append(
      crearCelda(cancion.titulo),
      crearCelda(cancion.artista),
      crearCelda(formatear(cancion.duracion), "duracion"),
    );
    fila.addEventListener("dblclick", () => reproducir(indice));
    lista.append(fila);
  });
  marcarActiva();
}

function marcarActiva() {
  document.querySelectorAll("#canciones li").forEach((fila) => {
    fila.classList.toggle("activa", rutaActual !== null && fila.dataset.ruta === rutaActual);
  });
}

function mostrarBiblioteca(visible) {
  $("biblioteca").hidden = !visible;
  $("btn-pl").classList.toggle("activo", visible);
  if (visible) cargarLista();
}

function alternarBiblioteca() {
  mostrarBiblioteca($("biblioteca").hidden);
}

/* ---------- Acciones ---------- */

async function reproducir(indice) {
  const ok = await api.reproducir(indice);
  if (!ok) avisar("No se pudo reproducir esa canción");
  await refrescar();
}

async function elegirCarpeta() {
  const total = await api.elegir_carpeta();
  if (total === null) return;            // el usuario canceló
  avisar(`${contar(total)} ${total === 1 ? "cargada" : "cargadas"}`);
  mostrarBiblioteca(true);
  await refrescar();
}

/** Ejecuta una acción de Python y refresca la pantalla al instante. */
function accion(metodo) {
  return async () => {
    if (!api) return;
    await api[metodo]();
    await refrescar();
  };
}

/* ---------- Reloj: pregunta el estado a Python cada medio segundo ---------- */

async function pintar(e) {
  let texto;
  const arrastrando = $("progreso").dataset.arrastrando === "1";
  duracionActual = e.hay_cancion ? e.duracion : 0;

  if (!e.hay_cancion) {
    $("ahora-suena").textContent = "ahora suena: nada";
    if (!arrastrando) {
      pintarProgreso(0);
      $("tiempo").textContent = "0:00 / 0:00";
    }
    if (rutaActual !== null) {
      rutaActual = null;
      mostrarCaratula(null);
      marcarActiva();
    }
    if (e.fin) avisar("Fin de la lista");
    texto = `${contar(e.total)} en la biblioteca`;
  } else {
    $("ahora-suena").textContent = `ahora suena: ${e.titulo} - ${e.artista}`;
    if (!arrastrando) {
      const fraccion = e.duracion > 0 ? e.transcurrido / e.duracion : 0;
      pintarProgreso(fraccion);
      $("tiempo").textContent = `${formatear(e.transcurrido)} / ${formatear(e.duracion)}`;
    }

    if (e.ruta !== rutaActual) {          // cambió la canción: nueva carátula
      rutaActual = e.ruta;
      marcarActiva();
      mostrarCaratula(await api.caratula());
    }
    texto = e.en_pausa ? "En pausa" : `Reproduciendo · ${contar(e.total)}`;
  }

  if (performance.now() < avisoHasta) texto = avisoTexto;
  $("estado-texto").textContent = texto;
}

async function refrescar() {
  try {
    await pintar(await api.estado());
  } catch (error) {
    console.error(error);
  }
}

async function bucle() {
  await refrescar();
  setTimeout(bucle, 500);
}

/* ---------- Arranque ---------- */

window.addEventListener("pywebviewready", async () => {
  api = window.pywebview.api;
  ajustarVentana();

  const inicial = await api.estado();
  pintarVolumen(inicial.volumen / 100);
  await cargarLista();
  bucle();
});

$("btn-anterior").addEventListener("click", accion("anterior"));
$("btn-play").addEventListener("click", accion("reanudar"));
$("btn-pausa").addEventListener("click", accion("pausar"));
$("btn-stop").addEventListener("click", accion("detener"));
$("btn-siguiente").addEventListener("click", accion("siguiente"));

$("btn-navegar").addEventListener("click", elegirCarpeta);
$("btn-biblioteca").addEventListener("click", alternarBiblioteca);
$("btn-pl").addEventListener("click", alternarBiblioteca);
$("btn-subir").addEventListener("click", alternarBiblioteca);
$("btn-cerrar-lista").addEventListener("click", () => mostrarBiblioteca(false));
$("buscar").addEventListener("input", () => { if (api) cargarLista(); });

$("btn-ayuda").addEventListener("click", () => { $("ayuda").hidden = false; });
$("btn-cerrar-ayuda").addEventListener("click", () => { $("ayuda").hidden = true; });
$("ayuda").addEventListener("click", (e) => { if (e.target === $("ayuda")) $("ayuda").hidden = true; });
document.addEventListener("keydown", (e) => { if (e.key === "Escape") $("ayuda").hidden = true; });

$("btn-cerrar").addEventListener("click", () => { if (api) api.cerrar(); });