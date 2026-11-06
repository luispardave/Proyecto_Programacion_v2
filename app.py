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


from datetime import datetime

import pandas as pd
import streamlit as st

import estilos
import io_handler
from grafo import Grafo
from io_handler import formato_numero


st.set_page_config(page_title="Dijkstra-Visualizer",
                   page_icon=":material/hub:", layout="wide")

# ===== SECCIONES DEL MENU =====
SECCIONES = {
    "crear": "♖  1. Crear Grafo",
    "tabla": "♟  2. Matriz/Tabla",
    "dijkstra": "♞  3. Ejecutar Dijkstra",
    "historial": "♗  4. Historial",
    "ajustes": "♔  5. Ajustes",
}

# Grafo de ejemplo (el del boceto)
EJEMPLO = [("A", "B", 4), ("A", "C", 2), ("B", "C", 2), ("B", "D", 1),
           ("B", "E", 5), ("C", "D", 8), ("D", "E", 5)]

ss = st.session_state


# ===== ESTADO DE LA SESION =====
def iniciar_estado():
    """Crea las variables de la sesion la primera vez."""
    valores = {
        "nodos": [],          # ["A", "B", ...]
        "aristas": [],        # [{"origen", "destino", "peso"}, ...]
        "historial": [],      # recorridos ejecutados
        "resultado": None,    # ultimo Dijkstra ejecutado
        "dirigido": False,
        "tema": "Light",
    }
    if "nodos" not in ss:
        cargar_desde_csv(valores)
    for clave, valor in valores.items():
        if clave not in ss:
            ss[clave] = valor


def cargar_desde_csv(valores):
    """Al abrir o recargar la pagina, recupera el grafo guardado en
    Nodos.csv."""
    try:
        valores["nodos"], valores["aristas"] = io_handler.cargar_grafo_csv()
    except (ValueError, KeyError, OSError) as e:
        st.toast(f"No se pudo leer Nodos.csv: {e}", icon=":material/error:")


def guardar_en_csv():
    """Guarda el grafo actual en Nodos.csv para que no se pierda."""
    try:
        io_handler.guardar_grafo_csv(ss.nodos, ss.aristas)
    except PermissionError:
        avisar_error("No se pudo guardar Nodos.csv (¿está abierto en otro "
                     "programa?).")
    except OSError as e:
        avisar_error(f"No se pudo guardar Nodos.csv: {e}")


def grafo_actual():
    """Objeto Grafo (grafo.py) con los nodos y aristas de la sesion."""
    return Grafo.desde_listas(ss.nodos, ss.aristas, ss.dirigido)


def grafo_modificado():
    """Al cambiar el grafo se guarda en Nodos.csv y el ultimo resultado
    deja de ser valido."""
    ss.resultado = None
    guardar_en_csv()


def avisar_error(error):
    st.toast(str(error), icon=":material/error:")


def flecha():
    return " → " if ss.dirigido else " — "


# ===== CALLBACKS (se ejecutan antes de redibujar la pagina) =====
def cb_agregar_nodo():
    try:
        nombre = io_handler.validar_nodo(ss.nuevo_nodo)
    except io_handler.NodoInvalidoError as e:
        return avisar_error(e)
    if nombre in ss.nodos:
        return st.toast(f"El nodo {nombre} ya existe.", icon=":material/info:")
    ss.nodos = sorted(ss.nodos + [nombre])
    grafo_modificado()
    st.toast(f"Nodo {nombre} agregado.", icon=":material/check_circle:")


def cb_agregar_arista():
    origen, destino = ss.arista_origen, ss.arista_destino
    try:
        peso = io_handler.validar_peso(ss.arista_peso)
        nueva = io_handler.agregar_conexion(ss.aristas, origen, destino,
                                            peso, ss.dirigido)
    except (io_handler.PesoInvalidoError,
            io_handler.ConexionInvalidaError) as e:
        return avisar_error(e)
    texto = f"{origen}{flecha()}{destino}"
    if nueva:
        st.toast(f"Conexión {texto} agregada.", icon=":material/check_circle:")
    else:
        st.toast(f"Peso de {texto} actualizado a {formato_numero(peso)}.",
                 icon=":material/edit:")
    grafo_modificado()


def cb_eliminar_nodo():
    nombre = ss.nodo_a_borrar
    ss.nodos.remove(nombre)
    ss.aristas = io_handler.quitar_nodo(ss.aristas, nombre)
    grafo_modificado()
    st.toast(f"Nodo {nombre} y sus conexiones eliminados.",
             icon=":material/delete:")


def cb_eliminar_arista():
    elegida = ss.arista_a_borrar
    ss.aristas = [a for a in ss.aristas
                  if io_handler.etiqueta_conexion(a, ss.dirigido) != elegida]
    grafo_modificado()
    st.toast("Conexión eliminada.", icon=":material/delete:")


def cb_cargar_ejemplo():
    ss.nodos = ["A", "B", "C", "D", "E"]
    ss.aristas = [{"origen": o, "destino": d, "peso": p}
                  for o, d, p in EJEMPLO]
    grafo_modificado()
    st.toast("Grafo de ejemplo cargado.", icon=":material/check_circle:")


def cb_limpiar_grafo():
    ss.nodos = []
    ss.aristas = []
    grafo_modificado()


def cb_importar_csv():
    archivo = ss.get("csv_subido")
    if archivo is None:
        return st.toast("Primero selecciona un archivo CSV.",
                        icon=":material/info:")
    try:
        texto = archivo.getvalue().decode("utf-8-sig")
        nodos, aristas = io_handler.leer_conexiones_texto(texto)
    except KeyError as e:
        return avisar_error(f"Falta la columna {e} en el CSV.")
    except (ValueError, UnicodeDecodeError) as e:
        return avisar_error(f"CSV inválido: {e}")
    ss.nodos, ss.aristas = nodos, aristas
    grafo_modificado()
    st.toast(f"Se cargaron {len(aristas)} conexiones.",
             icon=":material/check_circle:")


def cb_ejecutar_dijkstra():
    inicio, destino = ss.ruta_inicio, ss.ruta_destino
    grafo = grafo_actual()
    distancia, camino = grafo.dijkstra(inicio, destino)
    distancias, _ = grafo.calcular_distancias(inicio)

    ss.resultado = {
        "inicio": inicio, "destino": destino, "distancia": distancia,
        "camino": camino, "distancias": distancias,
        "tramos": grafo.recorrido(camino),
    }
    ss.historial.insert(0, {
        "Hora": datetime.now().strftime("%H:%M:%S"),
        "Inicio": inicio,
        "Destino": destino,
        "Camino": " → ".join(camino) if camino else "Sin camino",
        "Peso total": formato_numero(distancia),
        "Tipo": "Dirigido" if ss.dirigido else "No dirigido",
    })


def cb_cambiar_dirigido():
    ss.dirigido = ss.dirigido_widget
    grafo_modificado()


def cb_reiniciar_todo():
    cb_limpiar_grafo()
    ss.historial = []
    st.toast("Se reinició toda la información.", icon=":material/restart_alt:")


# ===== LIENZO DEL GRAFO =====
def dibujar_lienzo(resultado=None, alto=470):
    """Dibuja el grafo como piezas sobre un tablero; si hay resultado
    resalta el camino y muestra las distancias."""
    c = estilos.PALETAS[ss.tema]

    with st.container(key="lienzo"):
        st.markdown('<span class="lienzo-titulo">♟ Tablero del grafo</span>',
                    unsafe_allow_html=True)
        if not ss.nodos:
            st.info("El tablero está vacío. Agrega nodos con el panel de la "
                    "derecha o carga el grafo de ejemplo.")
            st.button("Cargar grafo de ejemplo", on_click=cb_cargar_ejemplo,
                      icon=":material/auto_awesome:")
            return

        camino = resultado["camino"] if resultado else []
        tramos_camino = set()
        for origen, siguiente, _, _ in (resultado["tramos"] if resultado
                                        else []):
            tramos_camino.add((origen, siguiente))
            if not ss.dirigido:
                tramos_camino.add((siguiente, origen))

        posiciones = estilos.posiciones_circulares(ss.nodos)
        lista_nodos = []
        for i, nombre in enumerate(ss.nodos):
            es_inicio = resultado is not None and nombre == resultado["inicio"]
            es_destino = bool(camino) and nombre == resultado["destino"]
            pieza = (estilos.PIEZA_INICIO if es_inicio else
                     estilos.PIEZA_DESTINO if es_destino else
                     estilos.pieza_de(i))
            texto, titulo = nombre, f"Nodo {nombre}"
            if resultado:
                dist = formato_numero(resultado["distancias"][nombre])
                texto = f"{nombre} · {'Inicio' if es_inicio else dist}"
                titulo = f"Nodo {nombre} · dist: {dist}"
            color = (c["pieza_inicio"] if es_inicio else
                     c["dorado"] if nombre in camino else c["pieza"])
            x, y = posiciones[nombre]
            lista_nodos.append(estilos.nodo_pieza(nombre, pieza, texto, titulo,
                                                  color, x, y, c))

        lista_aristas = []
        for a in ss.aristas:
            en_camino = (a["origen"], a["destino"]) in tramos_camino
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


def titulo_panel(texto):
    st.markdown(f'<div class="titulo-panel">{texto}</div>',
                unsafe_allow_html=True)


def tabla_numerada(filas, inicio=1, paso=1):
    """Muestra una lista de dicts como tabla con indice desde 'inicio'."""
    tabla = pd.DataFrame(filas)
    tabla.index = range(inicio, inicio + paso * len(tabla), paso)
    st.table(tabla)


# ===== SECCION 1: CREAR GRAFO =====
def seccion_crear():
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
def seccion_tabla():
    titulo_panel("[ 2. Matriz de adyacencia y tabla de conexiones ]")

    if ss.nodos:
        st.markdown("**Matriz de adyacencia**")
        st.caption("Cada celda es el peso de ir de la fila a la columna "
                   "(· = sin conexión).")
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
                   "Nodos.csv). Importar reemplaza el grafo actual. El grafo "
                   "se guarda solo en Nodos.csv cada vez que cambia.")
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


# ===== SECCION 3: EJECUTAR DIJKSTRA =====
def seccion_dijkstra():
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

    resultado = ss.resultado
    col_lienzo, col_info = st.columns([3, 1.3], gap="medium")
    with col_lienzo:
        dibujar_lienzo(resultado, alto=440)

    with col_info:
        if resultado is None:
            st.caption("Elige inicio y destino y presiona **Ejecutar "
                       "Dijkstra** para ver el camino más corto.")
            return

        inicio, destino = resultado["inicio"], resultado["destino"]
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
def seccion_historial():
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
def seccion_ajustes():
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
def main():
    iniciar_estado()
    st.markdown(estilos.css(ss.tema), unsafe_allow_html=True)

    # Barra lateral (menu)
    with st.sidebar:
        st.markdown('<div class="titulo-app">♞<br>Dijkstra-Visualizer</div>'
                    '<div class="lema-app">El camino más corto del reino'
                    '</div>', unsafe_allow_html=True)
        seccion = st.radio("Menú", list(SECCIONES), key="seccion",
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
    with st.container(key="tarjeta"):
        {"crear": seccion_crear,
         "tabla": seccion_tabla,
         "dijkstra": seccion_dijkstra,
         "historial": seccion_historial,
         "ajustes": seccion_ajustes}[seccion]()


if __name__ == "__main__":
    main()
