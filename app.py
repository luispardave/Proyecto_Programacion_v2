"""
Titulo: app
Nombre Completo: Luis Angel Pardave Garcia
Fecha de creación: 05/11/2026
Descripcion: Web app en Streamlit (ALGO-VISUALIZER) para crear un grafo,
             verlo en un lienzo y ejecutar Dijkstra de forma visual.
             Ejecutar con:  streamlit run app.py
"""


import csv
import io
import math
from datetime import datetime

import pandas as pd
import streamlit as st
from streamlit_agraph import Config, Edge, Node, agraph

import estilos
from grafo import Grafo
from io_handler import (ENCABEZADOS, NodoInvalidoError, PesoInvalidoError,
                        validar_nodo, validar_peso)


st.set_page_config(page_title="Algo-Visualizer", page_icon=":material/hub:",
                   layout="wide")

# ===== SECCIONES DEL MENU =====
SECCIONES = {
    "crear": ":material/add_circle: 1. Crear Grafo",
    "tabla": ":material/table_chart: 2. Matriz/Tabla",
    "dijkstra": ":material/play_arrow: 3. Ejecutar Dijkstra",
    "historial": ":material/history: 4. Historial",
    "ajustes": ":material/settings: 5. Ajustes",
}

# Grafo de ejemplo (el del boceto)
EJEMPLO = [("A", "B", 4), ("A", "C", 2), ("B", "C", 2), ("B", "D", 1),
           ("B", "E", 5), ("C", "D", 8), ("D", "E", 5)]


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
    for clave, valor in valores.items():
        if clave not in st.session_state:
            st.session_state[clave] = valor


def construir_grafo():
    """Arma un objeto Grafo con los nodos y aristas de la sesion."""
    grafo = Grafo(dirigido=st.session_state.dirigido)
    for nombre in st.session_state.nodos:
        grafo.agregar_nodo(nombre)
    for a in st.session_state.aristas:
        grafo.agregar_conexion(a["origen"], a["destino"], a["peso"])
    return grafo


def buscar_arista(origen, destino):
    """Regresa la arista entre origen y destino (o None)."""
    for a in st.session_state.aristas:
        if a["origen"] == origen and a["destino"] == destino:
            return a
        if (not st.session_state.dirigido and a["origen"] == destino
                and a["destino"] == origen):
            return a
    return None


def grafo_modificado():
    """Al cambiar el grafo, el ultimo resultado ya no es valido."""
    st.session_state.resultado = None


def formato(numero):
    """Muestra 4 en vez de 4.0 y el infinito como simbolo."""
    if numero == float("inf"):
        return "∞"
    if float(numero).is_integer():
        return str(int(numero))
    return str(round(numero, 2))


def flecha():
    return " → " if st.session_state.dirigido else " — "


# ===== CALLBACKS (se ejecutan antes de redibujar la pagina) =====
def cb_agregar_nodo():
    try:
        nombre = validar_nodo(st.session_state.nuevo_nodo)
    except NodoInvalidoError as e:
        st.toast(str(e), icon=":material/error:")
        return
    if nombre in st.session_state.nodos:
        st.toast(f"El nodo {nombre} ya existe.", icon=":material/info:")
        return
    st.session_state.nodos.append(nombre)
    st.session_state.nodos.sort()
    grafo_modificado()
    st.toast(f"Nodo {nombre} agregado.", icon=":material/check_circle:")


def cb_agregar_arista():
    origen = st.session_state.arista_origen
    destino = st.session_state.arista_destino
    if origen == destino:
        st.toast("El origen y el destino no pueden ser iguales.",
                 icon=":material/error:")
        return
    try:
        peso = validar_peso(st.session_state.arista_peso)
    except PesoInvalidoError as e:
        st.toast(str(e), icon=":material/error:")
        return

    existente = buscar_arista(origen, destino)
    if existente:
        existente["peso"] = peso
        st.toast(f"Peso de {origen}{flecha()}{destino} actualizado a "
                 f"{formato(peso)}.", icon=":material/edit:")
    else:
        st.session_state.aristas.append(
            {"origen": origen, "destino": destino, "peso": peso})
        st.toast(f"Conexión {origen}{flecha()}{destino} agregada.",
                 icon=":material/check_circle:")
    grafo_modificado()


def cb_eliminar_nodo():
    nombre = st.session_state.nodo_a_borrar
    st.session_state.nodos.remove(nombre)
    st.session_state.aristas = [
        a for a in st.session_state.aristas
        if nombre not in (a["origen"], a["destino"])]
    grafo_modificado()
    st.toast(f"Nodo {nombre} y sus conexiones eliminados.",
             icon=":material/delete:")


def etiqueta_arista(a):
    return f"{a['origen']}{flecha()}{a['destino']}  (peso {formato(a['peso'])})"


def cb_eliminar_arista():
    elegida = st.session_state.arista_a_borrar
    st.session_state.aristas = [a for a in st.session_state.aristas
                                if etiqueta_arista(a) != elegida]
    grafo_modificado()
    st.toast("Conexión eliminada.", icon=":material/delete:")


def cb_cargar_ejemplo():
    st.session_state.nodos = ["A", "B", "C", "D", "E"]
    st.session_state.aristas = [
        {"origen": o, "destino": d, "peso": p} for o, d, p in EJEMPLO]
    grafo_modificado()
    st.toast("Grafo de ejemplo cargado.", icon=":material/check_circle:")


def cb_limpiar_grafo():
    st.session_state.nodos = []
    st.session_state.aristas = []
    grafo_modificado()


def cb_importar_csv():
    archivo = st.session_state.get("csv_subido")
    if archivo is None:
        st.toast("Primero selecciona un archivo CSV.", icon=":material/info:")
        return
    try:
        texto = archivo.getvalue().decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(texto))
        nodos, aristas = set(), []
        for num, row in enumerate(reader, start=2):
            try:
                origen = validar_nodo(row["origen"])
                destino = validar_nodo(row["destino"])
                peso = validar_peso(row["peso"])
            except (NodoInvalidoError, PesoInvalidoError) as e:
                raise ValueError(f"fila {num}: {e}")
            if origen == destino:
                raise ValueError(f"fila {num}: origen y destino iguales.")
            nodos.update([origen, destino])
            aristas.append({"origen": origen, "destino": destino,
                            "peso": peso})
    except KeyError as e:
        st.toast(f"Falta la columna {e} en el CSV.", icon=":material/error:")
        return
    except (ValueError, UnicodeDecodeError) as e:
        st.toast(f"CSV inválido: {e}", icon=":material/error:")
        return

    st.session_state.nodos = sorted(nodos)
    st.session_state.aristas = aristas
    grafo_modificado()
    st.toast(f"Se cargaron {len(aristas)} conexiones.",
             icon=":material/check_circle:")


def cb_ejecutar_dijkstra():
    inicio = st.session_state.ruta_inicio
    destino = st.session_state.ruta_destino
    grafo = construir_grafo()
    distancia, camino = grafo.dijkstra(inicio, destino)
    distancias, _ = grafo.calcular_distancias(inicio)

    tramos = []
    acumulado = 0
    for i in range(len(camino) - 1):
        peso = grafo.nodos[camino[i]].vecinos[camino[i + 1]]
        acumulado += peso
        tramos.append({"Tramo": f"{camino[i]}{flecha()}{camino[i + 1]}",
                       "Peso": formato(peso),
                       "Acumulado": formato(acumulado)})

    st.session_state.resultado = {
        "inicio": inicio, "destino": destino, "distancia": distancia,
        "camino": camino, "distancias": distancias, "tramos": tramos,
    }
    st.session_state.historial.insert(0, {
        "Hora": datetime.now().strftime("%H:%M:%S"),
        "Inicio": inicio,
        "Destino": destino,
        "Camino": " → ".join(camino) if camino else "Sin camino",
        "Peso total": formato(distancia),
        "Tipo": "Dirigido" if st.session_state.dirigido else "No dirigido",
    })


def cb_cambiar_dirigido():
    st.session_state.dirigido = st.session_state.dirigido_widget
    grafo_modificado()


def cb_reiniciar_todo():
    cb_limpiar_grafo()
    st.session_state.historial = []
    st.toast("Se reinició toda la información.", icon=":material/restart_alt:")


# ===== LIENZO DEL GRAFO =====
def posiciones_circulares(nodos):
    """Acomoda los nodos en circulo (despues se pueden arrastrar)."""
    n = len(nodos)
    radio = max(160, 45 * n)
    pos = {}
    for i, nombre in enumerate(nodos):
        angulo = math.pi + 2 * math.pi * i / max(n, 1)
        pos[nombre] = (radio * math.cos(angulo), radio * math.sin(angulo))
    return pos


def dibujar_lienzo(resultado=None, alto=470):
    """Dibuja el grafo; si hay resultado resalta el camino y distancias."""
    c = estilos.PALETAS[st.session_state.tema]
    nodos = st.session_state.nodos

    with st.container(key="lienzo"):
        st.markdown('<span class="lienzo-titulo">Graph Canvas</span>',
                    unsafe_allow_html=True)
        if not nodos:
            st.info("El lienzo está vacío. Agrega nodos con el panel de la "
                    "derecha o carga el grafo de ejemplo.")
            st.button("Cargar grafo de ejemplo", on_click=cb_cargar_ejemplo,
                      icon=":material/auto_awesome:")
            return

        camino = resultado["camino"] if resultado else []
        tramos_camino = set()
        for i in range(len(camino) - 1):
            tramos_camino.add((camino[i], camino[i + 1]))
            if not st.session_state.dirigido:
                tramos_camino.add((camino[i + 1], camino[i]))

        pos = posiciones_circulares(nodos)
        lista_nodos = []
        for nombre in nodos:
            es_inicio = resultado is not None and nombre == resultado["inicio"]
            en_camino = nombre in camino
            etiqueta = nombre
            titulo = nombre
            if resultado:
                dist = formato(resultado["distancias"][nombre])
                etiqueta = f"{nombre}\n{'START' if es_inicio else dist}"
                titulo = f"dist: {dist}"
            fondo = c["guinda"] if es_inicio else c["nodo_bg"]
            borde = c["dorado"] if (es_inicio or en_camino) else c["nodo_borde"]
            x, y = pos[nombre]
            lista_nodos.append(Node(
                id=nombre, label=etiqueta, title=titulo, shape="circle",
                x=x, y=y, borderWidth=4 if en_camino else 3,
                color={"background": fondo, "border": borde,
                       "highlight": {"background": fondo,
                                     "border": c["dorado"]}},
                font={"color": c["dorado"] if es_inicio else c["nodo_texto"],
                      "size": 20, "face": "Roboto", "bold": True},
                margin=14,
            ))

        lista_aristas = []
        for a in st.session_state.aristas:
            en_camino = (a["origen"], a["destino"]) in tramos_camino
            lista_aristas.append(Edge(
                source=a["origen"], target=a["destino"],
                label=formato(a["peso"]),
                color=c["dorado"] if en_camino else c["arista"],
                width=5 if en_camino else 2, smooth=False,
                font={"color": c["texto"], "size": 15, "face": "Roboto",
                      "strokeWidth": 4, "strokeColor": c["lienzo"]},
            ))

        config = Config(height=alto, width=700,
                        directed=st.session_state.dirigido, physics=False,
                        interaction={"dragNodes": True, "dragView": True,
                                     "zoomView": True, "hover": True})
        config.width = "100%"
        if st.session_state.dirigido:
            config.edges = {"arrows": "to"}
        agraph(nodes=lista_nodos, edges=lista_aristas, config=config)

    st.caption("* Arrastra los nodos para acomodarlos. Usa la rueda del "
               "mouse para hacer zoom.")


# ===== SECCION 1: CREAR GRAFO =====
def seccion_crear():
    st.markdown('<div class="titulo-panel">PANEL PRINCIPAL: '
                '[ 1. Creador de Grafo (Lienzo interactivo) ]</div>',
                unsafe_allow_html=True)
    col_lienzo, col_paneles = st.columns([3, 1.15], gap="medium")

    with col_lienzo:
        dibujar_lienzo(st.session_state.resultado)

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
            nodos = st.session_state.nodos
            if len(nodos) < 2:
                st.caption("Agrega al menos 2 nodos para conectarlos.")
            else:
                with st.form("form_arista", border=False):
                    st.selectbox("Origen:", nodos, key="arista_origen")
                    st.selectbox("Destino:", nodos, index=1,
                                 key="arista_destino")
                    st.text_input("Peso:", key="arista_peso",
                                  placeholder="Ej: 4")
                    st.form_submit_button("+ Conectar",
                                          on_click=cb_agregar_arista)


# ===== SECCION 2: MATRIZ / TABLA =====
def seccion_tabla():
    st.markdown('<div class="titulo-panel">[ 2. Matriz de adyacencia y '
                'tabla de conexiones ]</div>', unsafe_allow_html=True)
    nodos = st.session_state.nodos
    aristas = st.session_state.aristas

    if nodos:
        grafo = construir_grafo()
        st.markdown("**Matriz de adyacencia**")
        st.caption("Cada celda es el peso de ir de la fila a la columna "
                   "(· = sin conexión).")
        matriz = pd.DataFrame(
            [[formato(grafo.nodos[f].vecinos[col])
              if col in grafo.nodos[f].vecinos else "·"
              for col in nodos] for f in nodos],
            index=nodos, columns=nodos)
        st.table(matriz)

        st.markdown("**Tabla de conexiones**")
        if aristas:
            tabla = pd.DataFrame([{"Origen": a["origen"],
                                   "Destino": a["destino"],
                                   "Peso": formato(a["peso"])}
                                  for a in aristas])
            tabla.index = range(1, len(tabla) + 1)
            st.table(tabla)
        else:
            st.caption("Todavía no hay conexiones.")
    else:
        st.info("El grafo está vacío. Ve a **1. Crear Grafo** o importa un "
                "CSV.")

    st.divider()
    col_editar, col_csv = st.columns(2, gap="large")

    with col_editar:
        st.markdown("**Eliminar elementos**")
        if nodos:
            c1, c2 = st.columns([2, 1], vertical_alignment="bottom")
            c1.selectbox("Nodo", nodos, key="nodo_a_borrar")
            c2.button("Eliminar nodo", on_click=cb_eliminar_nodo,
                      icon=":material/delete:", width="stretch")
        if aristas:
            c1, c2 = st.columns([2, 1], vertical_alignment="bottom")
            c1.selectbox("Conexión", [etiqueta_arista(a) for a in aristas],
                         key="arista_a_borrar")
            c2.button("Eliminar conexión", on_click=cb_eliminar_arista,
                      icon=":material/delete:", width="stretch")
        if nodos:
            st.button("Vaciar grafo", on_click=cb_limpiar_grafo,
                      icon=":material/delete_sweep:")
        else:
            st.caption("No hay nada que eliminar.")

    with col_csv:
        st.markdown("**Importar / Exportar CSV**")
        st.caption(f"Columnas: {', '.join(ENCABEZADOS)} (como Nodos.csv). "
                   "Importar reemplaza el grafo actual.")
        st.file_uploader("Archivo CSV", type="csv", key="csv_subido",
                         label_visibility="collapsed")
        c1, c2 = st.columns(2)
        c1.button("Importar", on_click=cb_importar_csv,
                  icon=":material/upload:", width="stretch")
        salida = io.StringIO()
        writer = csv.DictWriter(salida, fieldnames=ENCABEZADOS)
        writer.writeheader()
        writer.writerows(aristas)
        c2.download_button("Exportar", salida.getvalue(), file_name="Nodos.csv",
                           mime="text/csv", icon=":material/download:",
                           disabled=not aristas, width="stretch")


# ===== SECCION 3: EJECUTAR DIJKSTRA =====
def seccion_dijkstra():
    st.markdown('<div class="titulo-panel">[ 3. Ejecutar Dijkstra ]</div>',
                unsafe_allow_html=True)
    nodos = st.session_state.nodos
    if len(nodos) < 2:
        st.info("Necesitas al menos 2 nodos. Ve a **1. Crear Grafo**.")
        return

    c1, c2, c3 = st.columns([1, 1, 1], vertical_alignment="bottom")
    c1.selectbox("Nodo de inicio", nodos, key="ruta_inicio")
    c2.selectbox("Nodo de destino", nodos, index=len(nodos) - 1,
                 key="ruta_destino")
    c3.button("Ejecutar Dijkstra", type="primary", icon=":material/play_arrow:",
              on_click=cb_ejecutar_dijkstra, width="stretch")

    resultado = st.session_state.resultado
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
                      formato(resultado["distancia"]))
            if resultado["tramos"]:
                st.markdown("**Recorrido tramo por tramo**")
                tabla = pd.DataFrame(resultado["tramos"])
                tabla.index = range(1, len(tabla) + 1)
                st.table(tabla)

        st.markdown(f"**Distancia mínima desde {inicio}**")
        dist = pd.DataFrame(
            {"Distancia": [formato(d) for d in
                           resultado["distancias"].values()]},
            index=list(resultado["distancias"].keys()))
        st.table(dist)


# ===== SECCION 4: HISTORIAL =====
def seccion_historial():
    st.markdown('<div class="titulo-panel">[ 4. Historial de recorridos ]'
                '</div>', unsafe_allow_html=True)
    historial = st.session_state.historial
    if not historial:
        st.info("Aún no has ejecutado Dijkstra en esta sesión.")
        return
    st.caption(f"{len(historial)} recorrido(s) en esta sesión, del más "
               "reciente al más antiguo.")
    tabla = pd.DataFrame(historial)
    tabla.index = range(len(tabla), 0, -1)
    st.table(tabla)
    if st.button("Borrar historial", icon=":material/delete:"):
        st.session_state.historial = []
        st.rerun()


# ===== SECCION 5: AJUSTES =====
def seccion_ajustes():
    st.markdown('<div class="titulo-panel">[ 5. Ajustes ]</div>',
                unsafe_allow_html=True)

    st.markdown("**Tipo de grafo**")
    st.toggle("Grafo dirigido (las conexiones solo van de origen a destino)",
              value=st.session_state.dirigido, key="dirigido_widget",
              on_change=cb_cambiar_dirigido)

    st.markdown("**Tema**")
    st.caption("Cambia entre Light y Dark con el selector de arriba a la "
               "derecha.")

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
    st.markdown(estilos.css(st.session_state.tema), unsafe_allow_html=True)

    # Barra lateral (menu)
    with st.sidebar:
        st.markdown('<div class="titulo-app">☰&nbsp; ALGO-VISUALIZER</div>',
                    unsafe_allow_html=True)
        seccion = st.radio("Menú", list(SECCIONES), key="seccion",
                           format_func=SECCIONES.get,
                           label_visibility="collapsed")

    # Encabezado
    col_titulo, col_modo = st.columns([3, 1], vertical_alignment="center")
    col_titulo.markdown('<div class="encabezado">[<b>ALGO-VISUALIZER</b> '
                        '// DIJKSTRA PATHFINDER]</div>',
                        unsafe_allow_html=True)
    with col_modo:
        c1, c2 = st.columns([1, 2], vertical_alignment="center")
        c1.markdown("Modos:")
        c2.radio("Modo", ["Light", "Dark"], key="tema", horizontal=True,
                 label_visibility="collapsed")

    # Contenido de la seccion elegida
    with st.container(key="tarjeta"):
        {"crear": seccion_crear,
         "tabla": seccion_tabla,
         "dijkstra": seccion_dijkstra,
         "historial": seccion_historial,
         "ajustes": seccion_ajustes}[seccion]()


if __name__ == "__main__":
    main()
