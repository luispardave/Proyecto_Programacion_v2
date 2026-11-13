"""
Titulo: app
Nombre Completo: Luis Angel Pardave Garcia
Fecha de creación: 05/11/2026
Descripcion: Web app en Streamlit (DIJKSTRA-VISUALIZER) para crear un grafo,
             verlo en un lienzo y ejecutar Dijkstra de forma visual.
             La logica vive en grafo.py, io_handler.py y estilos.py;
             este archivo solo arma la interfaz.
             Ejecutar con:  streamlit run app.py
"""


import copy
from collections.abc import Callable
from datetime import datetime
from typing import Any, TypedDict

import pandas as pd
import streamlit as st

import estilos
import io_handler
from grafo import Grafo
from io_handler import formato_numero


# ===== TIPOS DE DATOS =====
class Arista(TypedDict):
    """Conexion del grafo: {"origen": "A", "destino": "B", "peso": 4}."""
    origen: str
    destino: str
    peso: float


class Resultado(TypedDict):
    """Ultimo Dijkstra ejecutado."""
    inicio: str
    destino: str
    distancia: float
    camino: list[str]
    distancias: dict[str, float]
    tramos: list[tuple[str, str, float, float]]  # (origen, sig, peso, acum)


class Almacen(TypedDict):
    """Datos que quedan en memoria mientras el servidor este encendido."""
    nodos: list[str]
    aristas: list[Arista]
    error: str | None
    sin_guardar: bool


FilaHistorial = dict[str, str]


st.set_page_config(page_title="Dijkstra-Visualizer",
                   page_icon=":material/hub:", layout="wide")

# ===== SECCIONES DEL MENU =====
SECCIONES: dict[str, str] = {
    "crear": "♖  1. Crear Grafo",
    "tabla": "♟  2. Matriz/Tabla",
    "dijkstra": "♞  3. Ejecutar Dijkstra",
    "historial": "♗  4. Historial",
    "ajustes": "♔  5. Ajustes",
}

# Grafo de ejemplo (el del boceto)
EJEMPLO: list[tuple[str, str, float]] = [
    ("A", "B", 4), ("A", "C", 2), ("B", "C", 2), ("B", "D", 1),
    ("B", "E", 5), ("C", "D", 8), ("D", "E", 5),
]

ss: Any = st.session_state   # variables de la sesion (nodos, aristas, ...)


# ===== ALMACEN EN MEMORIA (1 sola lectura de Nodos.csv) =====
@st.cache_resource
def almacen() -> Almacen:
    """Lee Nodos.csv UNA sola vez mientras el servidor de Streamlit este
    encendido. El diccionario que regresa queda en memoria y se comparte
    entre recargas (F5) y pestañas, asi el archivo no se vuelve a abrir."""
    datos: Almacen = {"nodos": [], "aristas": [], "error": None,
                      "sin_guardar": False}
    try:
        datos["nodos"], datos["aristas"] = io_handler.cargar_grafo_csv()
    except (ValueError, KeyError, OSError) as e:
        datos["error"] = f"No se pudo leer Nodos.csv: {e}"
    return datos


# ===== ESTADO DE LA SESION =====
def iniciar_estado() -> None:
    """Crea las variables de la sesion la primera vez, copiando el grafo
    desde el almacen en memoria (no desde el archivo)."""
    datos: Almacen = almacen()
    valores: dict[str, Any] = {
        "nodos": copy.deepcopy(datos["nodos"]),      # ["A", "B", ...]
        "aristas": copy.deepcopy(datos["aristas"]),  # [{origen, destino..}]
        "historial": [],      # recorridos ejecutados
        "resultado": None,    # ultimo Dijkstra ejecutado
        "dirigido": False,
        "tema": "Light",
    }
    if "nodos" not in ss and datos["error"]:
        st.toast(datos["error"], icon=":material/error:")
        datos["error"] = None   # avisar solo una vez
    for clave, valor in valores.items():
        if clave not in ss:
            ss[clave] = valor


def guardar_en_csv() -> bool:
    """Escribe el grafo actual en Nodos.csv (solo al presionar el boton
    'Guardar en Nodos.csv'). Regresa True si se guardo."""
    try:
        io_handler.guardar_grafo_csv(ss.nodos, ss.aristas)
    except PermissionError:
        avisar_error("No se pudo guardar Nodos.csv (¿está abierto en otro "
                     "programa?).")
        return False
    except OSError as e:
        avisar_error(f"No se pudo guardar Nodos.csv: {e}")
        return False
    almacen()["sin_guardar"] = False
    return True


def grafo_actual() -> Grafo:
    """Objeto Grafo (grafo.py) con los nodos y aristas de la sesion."""
    return Grafo.desde_listas(ss.nodos, ss.aristas, ss.dirigido)


def grafo_modificado() -> None:
    """Al cambiar el grafo se actualiza el almacen en memoria (para que
    sobreviva a una recarga) sin tocar Nodos.csv, y el ultimo resultado
    deja de ser valido."""
    ss.resultado = None
    datos: Almacen = almacen()
    datos["nodos"] = copy.deepcopy(ss.nodos)
    datos["aristas"] = copy.deepcopy(ss.aristas)
    datos["sin_guardar"] = True


def avisar_error(error: Exception | str) -> None:
    """Muestra un aviso rojo con el mensaje del error."""
    st.toast(str(error), icon=":material/error:")


def flecha() -> str:
    """Separador entre nodos segun el tipo de grafo."""
    return " → " if ss.dirigido else " — "


# ===== CALLBACKS (se ejecutan antes de redibujar la pagina) =====
def cb_agregar_nodo() -> None:
    try:
        nombre: str = io_handler.validar_nodo(ss.nuevo_nodo)
    except io_handler.NodoInvalidoError as e:
        avisar_error(e)
        return
    if nombre in ss.nodos:
        st.toast(f"El nodo {nombre} ya existe.", icon=":material/info:")
        return
    ss.nodos = sorted(ss.nodos + [nombre])
    grafo_modificado()
    st.toast(f"Nodo {nombre} agregado.", icon=":material/check_circle:")


def cb_agregar_arista() -> None:
    origen: str = ss.arista_origen
    destino: str = ss.arista_destino
    try:
        peso: float = io_handler.validar_peso(ss.arista_peso)
        nueva: bool = io_handler.agregar_conexion(ss.aristas, origen,
                                                  destino, peso, ss.dirigido)
    except (io_handler.PesoInvalidoError,
            io_handler.ConexionInvalidaError) as e:
        avisar_error(e)
        return
    texto: str = f"{origen}{flecha()}{destino}"
    if nueva:
        st.toast(f"Conexión {texto} agregada.", icon=":material/check_circle:")
    else:
        st.toast(f"Peso de {texto} actualizado a {formato_numero(peso)}.",
                 icon=":material/edit:")
    grafo_modificado()


def cb_eliminar_nodo() -> None:
    nombre: str = ss.nodo_a_borrar
    ss.nodos.remove(nombre)
    ss.aristas = io_handler.quitar_nodo(ss.aristas, nombre)
    grafo_modificado()
    st.toast(f"Nodo {nombre} y sus conexiones eliminados.",
             icon=":material/delete:")


def cb_eliminar_arista() -> None:
    elegida: str = ss.arista_a_borrar
    ss.aristas = [a for a in ss.aristas
                  if io_handler.etiqueta_conexion(a, ss.dirigido) != elegida]
    grafo_modificado()
    st.toast("Conexión eliminada.", icon=":material/delete:")


def cb_cargar_ejemplo() -> None:
    ss.nodos = ["A", "B", "C", "D", "E"]
    ss.aristas = [{"origen": o, "destino": d, "peso": p}
                  for o, d, p in EJEMPLO]
    grafo_modificado()
    st.toast("Grafo de ejemplo cargado.", icon=":material/check_circle:")


def cb_limpiar_grafo() -> None:
    ss.nodos = []
    ss.aristas = []
    grafo_modificado()


def cb_importar_csv() -> None:
    archivo = ss.get("csv_subido")   # UploadedFile | None
    if archivo is None:
        st.toast("Primero selecciona un archivo CSV.", icon=":material/info:")
        return
    try:
        texto: str = archivo.getvalue().decode("utf-8-sig")
        nodos: list[str]
        aristas: list[Arista]
        nodos, aristas = io_handler.leer_conexiones_texto(texto)
    except KeyError as e:
        avisar_error(f"Falta la columna {e} en el CSV.")
        return
    except (ValueError, UnicodeDecodeError) as e:
        avisar_error(f"CSV inválido: {e}")
        return
    ss.nodos, ss.aristas = nodos, aristas
    grafo_modificado()
    st.toast(f"Se cargaron {len(aristas)} conexiones.",
             icon=":material/check_circle:")


def cb_guardar_csv() -> None:
    if guardar_en_csv():
        st.toast("Grafo guardado en Nodos.csv.", icon=":material/save:")


def cb_ejecutar_dijkstra() -> None:
    inicio: str = ss.ruta_inicio
    destino: str = ss.ruta_destino
    grafo: Grafo = grafo_actual()
    distancia: float
    camino: list[str]
    distancia, camino = grafo.dijkstra(inicio, destino)
    distancias: dict[str, float]
    distancias, _ = grafo.calcular_distancias(inicio)

    resultado: Resultado = {
        "inicio": inicio, "destino": destino, "distancia": distancia,
        "camino": camino, "distancias": distancias,
        "tramos": grafo.recorrido(camino),
    }
    ss.resultado = resultado
    fila: FilaHistorial = {
        "Hora": datetime.now().strftime("%H:%M:%S"),
        "Inicio": inicio,
        "Destino": destino,
        "Camino": " → ".join(camino) if camino else "Sin camino",
        "Peso total": formato_numero(distancia),
        "Tipo": "Dirigido" if ss.dirigido else "No dirigido",
    }
    ss.historial.insert(0, fila)


def cb_cambiar_dirigido() -> None:
    ss.dirigido = ss.dirigido_widget
    grafo_modificado()


def cb_reiniciar_todo() -> None:
    cb_limpiar_grafo()
    ss.historial = []
    st.toast("Se reinició toda la información.", icon=":material/restart_alt:")


# ===== LIENZO DEL GRAFO =====
def dibujar_lienzo(resultado: Resultado | None = None,
                   alto: int = 470) -> None:
    """Dibuja el grafo como piezas sobre un tablero; si hay resultado
    resalta el camino y muestra las distancias."""
    c: dict[str, str] = estilos.PALETAS[ss.tema]

    with st.container(key="lienzo"):
        st.markdown('<span class="lienzo-titulo">♟ Tablero del grafo</span>',
                    unsafe_allow_html=True)
        if not ss.nodos:
            st.info("El tablero está vacío. Agrega nodos con el panel de la "
                    "derecha o carga el grafo de ejemplo.")
            st.button("Cargar grafo de ejemplo", on_click=cb_cargar_ejemplo,
                      icon=":material/auto_awesome:")
            return

        camino: list[str] = resultado["camino"] if resultado else []
        tramos_camino: set[tuple[str, str]] = set()
        for origen, siguiente, _, _ in (resultado["tramos"] if resultado
                                        else []):
            tramos_camino.add((origen, siguiente))
            if not ss.dirigido:
                tramos_camino.add((siguiente, origen))

        posiciones: dict[str, tuple[float, float]] = (
            estilos.posiciones_circulares(ss.nodos))
        lista_nodos: list[dict[str, Any]] = []
        for i, nombre in enumerate(ss.nodos):
            es_inicio: bool = (resultado is not None
                               and nombre == resultado["inicio"])
            es_destino: bool = (resultado is not None and bool(camino)
                                and nombre == resultado["destino"])
            pieza: str = (estilos.PIEZA_INICIO if es_inicio else
                          estilos.PIEZA_DESTINO if es_destino else
                          estilos.pieza_de(i))
            texto: str = nombre
            titulo: str = f"Nodo {nombre}"
            if resultado:
                dist: str = formato_numero(resultado["distancias"][nombre])
                texto = f"{nombre} · {'Inicio' if es_inicio else dist}"
                titulo = f"Nodo {nombre} · dist: {dist}"
            color: str = (c["pieza_inicio"] if es_inicio else
                          c["dorado"] if nombre in camino else c["pieza"])
            x, y = posiciones[nombre]
            lista_nodos.append(estilos.nodo_pieza(nombre, pieza, texto, titulo,
                                                  color, x, y, c))

        lista_aristas: list[dict[str, Any]] = []
        for a in ss.aristas:
            en_camino: bool = (a["origen"], a["destino"]) in tramos_camino
            lista_aristas.append(estilos.arista_lienzo(
                a["origen"], a["destino"], formato_numero(a["peso"]),
                en_camino, c))

        # El HTML solo lleva datos validados (letras y numeros del grafo)
        st.iframe(estilos.html_lienzo(lista_nodos, lista_aristas,
                                      ss.dirigido, c, alto),
                  height=alto)

    st.caption(f"{estilos.PIEZA_INICIO} inicio · {estilos.PIEZA_DESTINO} "
               "destino · piezas y línea doradas: camino más corto. Arrastra "
               "las piezas para acomodarlas y usa la rueda del mouse para "
               "hacer zoom.")


def titulo_panel(texto: str) -> None:
    """Titulo con estilo para el encabezado de cada seccion."""
    st.markdown(f'<div class="titulo-panel">{texto}</div>',
                unsafe_allow_html=True)


def tabla_numerada(filas: list[dict[str, str]], inicio: int = 1,
                   paso: int = 1) -> None:
    """Muestra una lista de dicts como tabla con indice desde 'inicio'."""
    tabla: pd.DataFrame = pd.DataFrame(filas)
    tabla.index = range(inicio, inicio + paso * len(tabla), paso)
    st.table(tabla)


# ===== SECCION 1: CREAR GRAFO =====
def seccion_crear() -> None:
    titulo_panel("PANEL PRINCIPAL: [ 1. Creador de Grafo "
                 "(Lienzo interactivo) ]")
    col_lienzo, col_paneles = st.columns([3, 1.15], gap="medium")

    with col_lienzo:
        dibujar_lienzo(ss.resultado)

    with col_paneles:
        with st.container(key="panel_nodo"):
            st.markdown("**AGREGAR NODO**")
            with st.form("form_nodo", clear_on_submit=True, border=False):
                st.text_input("Name:", key="nuevo_nodo", max_chars=1,
                              placeholder="Ej: C")
                st.form_submit_button("+ Añadir", on_click=cb_agregar_nodo)

        st.write("")
        with st.container(key="panel_arista"):
            st.markdown("**AGREGAR ARISTA**")
            if len(ss.nodos) < 2:
                st.caption("Agrega al menos 2 nodos para conectarlos.")
            else:
                with st.form("form_arista", border=False):
                    st.selectbox("Origen:", ss.nodos, key="arista_origen")
                    st.selectbox("Destino:", ss.nodos, index=1,
                                 key="arista_destino")
                    st.text_input("Peso:", key="arista_peso",
                                  placeholder="Ej: 4")
                    st.form_submit_button("+ Conectar",
                                          on_click=cb_agregar_arista)


# ===== SECCION 2: MATRIZ / TABLA =====
def seccion_tabla() -> None:
    titulo_panel("[ 2. Matriz de adyacencia y tabla de conexiones ]")

    if ss.nodos:
        st.markdown("**Matriz de adyacencia**")
        st.caption("Cada celda es el peso de ir de la fila a la columna "
                   "(· = sin conexión).")
        orden: list[str]
        matriz: list[list[float | None]]
        orden, matriz = grafo_actual().matriz_adyacencia(ss.nodos)
        st.table(pd.DataFrame(
            [["·" if p is None else formato_numero(p) for p in fila]
             for fila in matriz], index=orden, columns=orden))

        st.markdown("**Tabla de conexiones**")
        if ss.aristas:
            tabla_numerada([{"Origen": a["origen"], "Destino": a["destino"],
                             "Peso": formato_numero(a["peso"])}
                            for a in ss.aristas])
        else:
            st.caption("Todavía no hay conexiones.")
    else:
        st.info("El grafo está vacío. Ve a **1. Crear Grafo** o importa un "
                "CSV.")

    st.divider()
    col_editar, col_csv = st.columns(2, gap="large")

    with col_editar:
        st.markdown("**Eliminar elementos**")
        if ss.nodos:
            c1, c2 = st.columns([2, 1], vertical_alignment="bottom")
            c1.selectbox("Nodo", ss.nodos, key="nodo_a_borrar")
            c2.button("Eliminar nodo", on_click=cb_eliminar_nodo,
                      icon=":material/delete:", width="stretch")
        if ss.aristas:
            c1, c2 = st.columns([2, 1], vertical_alignment="bottom")
            c1.selectbox("Conexión",
                         [io_handler.etiqueta_conexion(a, ss.dirigido)
                          for a in ss.aristas],
                         key="arista_a_borrar")
            c2.button("Eliminar conexión", on_click=cb_eliminar_arista,
                      icon=":material/delete:", width="stretch")
        if ss.nodos:
            st.button("Vaciar grafo", on_click=cb_limpiar_grafo,
                      icon=":material/delete_sweep:")
        else:
            st.caption("No hay nada que eliminar.")

    with col_csv:
        st.markdown("**Importar / Exportar CSV**")
        st.caption(f"Columnas: {', '.join(io_handler.ENCABEZADOS)} (como "
                   "Nodos.csv). Importar reemplaza el grafo actual. "
                   "Nodos.csv se lee una sola vez al iniciar la app; los "
                   "cambios se escriben solo con **Guardar en Nodos.csv**.")
        st.file_uploader("Archivo CSV", type="csv", key="csv_subido",
                         label_visibility="collapsed")
        c1, c2 = st.columns(2)
        c1.button("Importar", on_click=cb_importar_csv,
                  icon=":material/upload:", width="stretch")
        c2.download_button("Exportar",
                           io_handler.conexiones_a_texto(ss.aristas,
                                                         ss.nodos),
                           file_name="Nodos.csv", mime="text/csv",
                           icon=":material/download:",
                           disabled=not ss.nodos, width="stretch")
        st.button("Guardar en Nodos.csv", on_click=cb_guardar_csv,
                  type="primary", icon=":material/save:", width="stretch")
        if almacen()["sin_guardar"]:
            st.caption(":orange[Hay cambios sin guardar en Nodos.csv.]")


# ===== SECCION 3: EJECUTAR DIJKSTRA =====
def seccion_dijkstra() -> None:
    titulo_panel("[ 3. Ejecutar Dijkstra ]")
    if len(ss.nodos) < 2:
        st.info("Necesitas al menos 2 nodos. Ve a **1. Crear Grafo**.")
        return

    c1, c2, c3 = st.columns(3, vertical_alignment="bottom")
    c1.selectbox("Nodo de inicio", ss.nodos, key="ruta_inicio")
    c2.selectbox("Nodo de destino", ss.nodos, index=len(ss.nodos) - 1,
                 key="ruta_destino")
    c3.button("Ejecutar Dijkstra", type="primary",
              icon=":material/play_arrow:",
              on_click=cb_ejecutar_dijkstra, width="stretch")

    resultado: Resultado | None = ss.resultado
    col_lienzo, col_info = st.columns([3, 1.3], gap="medium")
    with col_lienzo:
        dibujar_lienzo(resultado, alto=440)

    with col_info:
        if resultado is None:
            st.caption("Elige inicio y destino y presiona **Ejecutar "
                       "Dijkstra** para ver el camino más corto.")
            return

        inicio: str = resultado["inicio"]
        destino: str = resultado["destino"]
        if not resultado["camino"]:
            st.error(f"No existe un camino de {inicio} a {destino}.")
        else:
            st.markdown('<div class="etiqueta">Camino más corto</div>'
                        f'<div class="camino">'
                        f'{" → ".join(resultado["camino"])}</div>',
                        unsafe_allow_html=True)
            st.metric(f"Peso total de {inicio} a {destino}",
                      formato_numero(resultado["distancia"]))
            if resultado["tramos"]:
                st.markdown("**Recorrido tramo por tramo**")
                tabla_numerada([{"Tramo": f"{o}{flecha()}{s}",
                                 "Peso": formato_numero(p),
                                 "Acumulado": formato_numero(acum)}
                                for o, s, p, acum in resultado["tramos"]])

        st.markdown(f"**Distancia mínima desde {inicio}**")
        st.table(pd.DataFrame(
            {"Distancia": [formato_numero(d) for d in
                           resultado["distancias"].values()]},
            index=list(resultado["distancias"])))


# ===== SECCION 4: HISTORIAL =====
def seccion_historial() -> None:
    titulo_panel("[ 4. Historial de recorridos ]")
    if not ss.historial:
        st.info("Aún no has ejecutado Dijkstra en esta sesión.")
        return
    st.caption(f"{len(ss.historial)} recorrido(s) en esta sesión, del más "
               "reciente al más antiguo.")
    tabla_numerada(ss.historial, inicio=len(ss.historial), paso=-1)
    if st.button("Borrar historial", icon=":material/delete:"):
        ss.historial = []
        st.rerun()


# ===== SECCION 5: AJUSTES =====
def seccion_ajustes() -> None:
    titulo_panel("[ 5. Ajustes ]")

    st.markdown("**Tipo de grafo**")
    st.toggle("Grafo dirigido (las conexiones solo van de origen a destino)",
              value=ss.dirigido, key="dirigido_widget",
              on_change=cb_cambiar_dirigido)

    st.markdown("**Tema**")
    st.caption("Cambia entre Día (pergamino) y Noche (castillo) con el "
               "selector de arriba a la derecha.")

    st.markdown("**Datos**")
    c1, c2, _ = st.columns([1, 1, 2])
    c1.button("Cargar grafo de ejemplo", on_click=cb_cargar_ejemplo,
              icon=":material/auto_awesome:", width="stretch")
    c2.button("Reiniciar todo", on_click=cb_reiniciar_todo,
              icon=":material/restart_alt:", width="stretch")
    st.caption("Reiniciar borra el grafo y el historial de la sesión.")


# ===== PAGINA PRINCIPAL =====
def main() -> None:
    iniciar_estado()
    st.markdown(estilos.css(ss.tema), unsafe_allow_html=True)

    # Barra lateral (menu)
    with st.sidebar:
        st.markdown('<div class="titulo-app">♞<br>Dijkstra-Visualizer</div>'
                    '<div class="lema-app">El camino más corto del reino'
                    '</div>', unsafe_allow_html=True)
        seccion: str = st.radio("Menú", list(SECCIONES), key="seccion",
                                format_func=SECCIONES.get,
                                label_visibility="collapsed")

    # Encabezado
    col_titulo, col_modo = st.columns([3, 1], vertical_alignment="center")
    col_titulo.markdown('<div class="encabezado">⚜ <b>DIJKSTRA-VISUALIZER</b> '
                        '// DIJKSTRA PATHFINDER ⚜<small>Traza rutas entre '
                        'las casillas de tu tablero</small></div>',
                        unsafe_allow_html=True)
    with col_modo, st.container(key="modo"):
        c1, c2 = st.columns([1, 2], vertical_alignment="center")
        c1.markdown("Modos:")
        c2.radio("Modo", list(estilos.TEMAS), key="tema", horizontal=True,
                 format_func=estilos.TEMAS.get, label_visibility="collapsed")

    # Contenido de la seccion elegida
    paginas: dict[str, Callable[[], None]] = {
        "crear": seccion_crear,
        "tabla": seccion_tabla,
        "dijkstra": seccion_dijkstra,
        "historial": seccion_historial,
        "ajustes": seccion_ajustes,
    }
    with st.container(key="tarjeta"):
        paginas[seccion]()


if __name__ == "__main__":
    main()
