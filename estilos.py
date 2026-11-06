"""
Titulo: estilos
Nombre Completo: Luis Angel Pardave Garcia
Fecha de creación: 05/11/2026
Descripcion: Tematica medieval / ajedrez de la web app: paletas de color
             (Dia = pergamino, Noche = castillo), CSS y acomodo visual de
             los nodos en el lienzo
"""


import json
import math
from string import Template


# ===== NOMBRES VISIBLES DE LOS TEMAS =====
TEMAS = {"Light": "☀ Día", "Dark": "☾ Noche"}

# ===== PIEZAS DE AJEDREZ USADAS EN EL LIENZO =====
# "︎" pide que se dibuje como simbolo de texto y no como emoji
PIEZA_INICIO = "♚︎"     # Rey: de donde parte el recorrido
PIEZA_DESTINO = "♜︎"    # Torre: el castillo al que se quiere llegar
PIEZAS = ["♞︎", "♝︎", "♛︎", "♟︎"]  # resto de nodos
FUENTE_LIENZO = "Cinzel, Georgia, serif"
FUENTE_PIEZAS = "'Segoe UI Symbol', 'DejaVu Sans', 'Noto Sans Symbols2', serif"
VIS_NETWORK_JS = ("https://unpkg.com/vis-network@9.1.9/standalone/umd/"
                  "vis-network.min.js")


# ===== PALETAS DE COLOR =====
PALETAS = {
    # Dia: pergamino, tinta y lacre
    "Light": {
        "fondo": "#E9DCBE",
        "tarjeta": "#F7EFDC",
        "texto": "#2B1D12",
        "texto_suave": "#6E5A43",
        "guinda": "#6B1420",
        "acento": "#6B1420",
        "dorado": "#B8892E",
        "sidebar": "#24160D",
        "sidebar2": "#3E2716",
        "madera": "#3E2716",
        "madera2": "#2A1A0F",
        "panel_texto": "#F3E6C8",
        "borde": "#CDB284",
        "lienzo": "#F4EAD2",
        "casilla": "#E2D0A8",
        "marco": "#5A3A1E",
        "nodo_bg": "#FBF5E6",
        "nodo_borde": "#6B1420",
        "nodo_texto": "#2B1D12",
        "arista": "#4A3322",
        "input_bg": "#FFFAF0",
        "input_texto": "#2B1D12",
        "fila_par": "#F1E6CC",
        "pieza": "#2B1D12",
        "pieza_inicio": "#8C1C2B",
    },
    # Noche: piedra de castillo a la luz de las antorchas
    "Dark": {
        "fondo": "#121010",
        "tarjeta": "#1D1916",
        "texto": "#EADBB8",
        "texto_suave": "#A8977A",
        "guinda": "#8C1C2B",
        "acento": "#D4A848",
        "dorado": "#D4A848",
        "sidebar": "#0B0908",
        "sidebar2": "#1E1610",
        "madera": "#2E2014",
        "madera2": "#1E150D",
        "panel_texto": "#EADBB8",
        "borde": "#4A3B2A",
        "lienzo": "#1B1713",
        "casilla": "#29221C",
        "marco": "#3E2A18",
        "nodo_bg": "#2A231D",
        "nodo_borde": "#D4A848",
        "nodo_texto": "#EADBB8",
        "arista": "#BFA98A",
        "input_bg": "#241E19",
        "input_texto": "#EADBB8",
        "fila_par": "#231E1A",
        "pieza": "#F3E6C8",
        "pieza_inicio": "#E8705F",
    },
}


# ===== CSS (se rellena con la paleta del tema activo) =====
_CSS = Template("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700&family=Cinzel+Decorative:wght@700&family=EB+Garamond:wght@400;500;600&display=swap');

/* ----- Base: pergamino / piedra ----- */
html, body, .stApp { font-family: 'EB Garamond', Georgia, serif; }
.stApp {
    color: $texto;
    background:
        radial-gradient(ellipse at center, transparent 55%, rgba(0, 0, 0, .18)),
        $fondo;
}
[data-testid="stHeader"] { background: transparent; }
.stApp .stMarkdown p, .stApp .stMarkdown li { font-size: 1.08rem; }

/* Todas las letras toman el color de texto del tema (contrario al fondo) */
.stApp, .stApp p, .stApp span, .stApp label, .stApp li, .stApp div,
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
.stApp input, .stApp textarea, .stApp small, .stApp td { color: $texto; }
.stApp input::placeholder { color: $texto_suave; opacity: .8; }
.stApp [data-testid="stCaptionContainer"],
.stApp [data-testid="stCaptionContainer"] p {
    color: $texto_suave; font-style: italic;
}

/* Menus desplegables de los selectbox */
[role="listbox"], [role="option"], [role="option"] * {
    background: $input_bg; color: $input_texto;
}
[role="option"]:hover, [role="option"][aria-selected="true"] {
    background: $fila_par;
}
.stMarkdown strong { font-family: 'Cinzel', serif; letter-spacing: .5px; }

/* ----- Barra lateral: madera oscura con filo dorado ----- */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, $sidebar2, $sidebar);
    border-right: 3px double $dorado;
}
.stApp [data-testid="stSidebar"] *, [data-testid="stSidebar"] * {
    color: #F3E6C8;
}
.titulo-app {
    font-family: 'Cinzel Decorative', 'Cinzel', serif; font-size: 1.3rem;
    color: $dorado !important; text-align: center; line-height: 1.3;
    padding: .3rem 0 .2rem 0;
}
.lema-app {
    text-align: center; font-style: italic; font-size: .95rem;
    color: #CDB284 !important; padding-bottom: .6rem; margin-bottom: .8rem;
    border-bottom: 1px solid rgba(212, 168, 72, .45);
}
[data-testid="stSidebar"] [role="radiogroup"] { gap: .3rem; width: 100%; }
[data-testid="stSidebar"] [role="radiogroup"] label {
    width: 100%; padding: .65rem .9rem; border-radius: 3px;
    border-left: 4px solid transparent; cursor: pointer;
}
[data-testid="stSidebar"] [role="radiogroup"] label > div:first-child {
    display: none;
}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
    background: rgba(212, 168, 72, .14); border-left-color: $dorado;
}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) p {
    color: $dorado;
}
[data-testid="stSidebar"] [role="radiogroup"] label:hover {
    background: rgba(212, 168, 72, .08);
}
[data-testid="stSidebar"] [role="radiogroup"] p {
    font-family: 'Cinzel', serif; font-size: 1rem; letter-spacing: .4px;
}

/* ----- Encabezado ----- */
.stApp .encabezado {
    font-family: 'Cinzel', serif; font-size: 1.15rem; letter-spacing: 1px;
    color: $texto;
}
.encabezado b { color: $acento; }
.encabezado small {
    display: block; font-family: 'EB Garamond', serif; font-style: italic;
    letter-spacing: 0; color: $texto_suave; font-size: .95rem;
}
.st-key-modo p { font-family: 'Cinzel', serif; }

/* ----- Tarjeta principal: pergamino con doble marco ----- */
.st-key-tarjeta {
    position: relative; background: $tarjeta; border-radius: 6px;
    padding: 1.6rem 1.8rem; border: 2px solid $dorado;
    box-shadow: inset 0 0 0 6px $tarjeta, inset 0 0 0 7px $borde,
                0 8px 24px rgba(0, 0, 0, .22);
}
.st-key-tarjeta::before, .st-key-tarjeta::after {
    content: "⚜"; position: absolute; color: $dorado; font-size: 1.3rem;
    line-height: 1;
}
.st-key-tarjeta::before { top: 10px; left: 14px; }
.st-key-tarjeta::after { bottom: 10px; right: 14px; }
.stApp .titulo-panel {
    font-family: 'Cinzel', serif; font-weight: 700; font-size: 1.25rem;
    color: $acento; letter-spacing: .8px; text-align: center;
    padding-bottom: .55rem; margin-bottom: .9rem;
    border-bottom: 1px solid $borde;
}
.titulo-panel::before { content: "♜  "; color: $dorado; }
.titulo-panel::after { content: "  ♜"; color: $dorado; }

/* ----- Lienzo: tablero de ajedrez con marco de madera ----- */
.st-key-lienzo {
    border: 10px solid $marco; outline: 2px solid $dorado;
    outline-offset: -2px; border-radius: 4px; padding: .5rem .7rem;
    background-color: $lienzo;
    background-image: conic-gradient($casilla 25%, transparent 0 50%,
                                     $casilla 0 75%, transparent 0);
    background-size: 90px 90px;
    box-shadow: 0 6px 16px rgba(0, 0, 0, .3);
}
.st-key-lienzo iframe { background: transparent; }
.stApp .lienzo-titulo {
    font-family: 'Cinzel', serif; font-weight: 700; color: $acento;
    background: $tarjeta; padding: .1rem .6rem; border: 1px solid $borde;
    border-radius: 3px;
}

/* ----- Paneles de madera (Agregar Nodo / Arista) ----- */
.st-key-panel_nodo, .st-key-panel_arista {
    background: linear-gradient(160deg, $madera, $madera2);
    border: 1px solid $dorado; border-radius: 6px; padding: 1.1rem 1.2rem;
    box-shadow: inset 0 0 0 4px $madera2,
                inset 0 0 0 5px rgba(212, 168, 72, .45),
                0 4px 12px rgba(0, 0, 0, .35);
}
.stApp .st-key-panel_nodo *, .stApp .st-key-panel_arista * {
    color: $panel_texto;
}
.stApp .st-key-panel_nodo strong, .stApp .st-key-panel_arista strong {
    color: $dorado; font-size: 1.05rem;
}
.st-key-panel_nodo [data-testid="stForm"],
.st-key-panel_arista [data-testid="stForm"] { border: none; padding: 0; }
.stApp .st-key-panel_nodo input, .stApp .st-key-panel_arista input {
    color: $input_texto !important;
}
.stApp .st-key-panel_nodo [data-baseweb="input"] > div,
.stApp .st-key-panel_arista [data-baseweb="input"] > div,
.stApp .st-key-panel_arista [data-testid="stSelectbox"] div:has(> input) {
    border-color: $dorado;
}
/* Solo los botones de enviar (no la flecha de las listas desplegables) */
.st-key-panel_nodo [data-testid="stFormSubmitButton"] button,
.st-key-panel_arista [data-testid="stFormSubmitButton"] button {
    background: transparent; border: 1px solid $dorado; width: 100%;
}
.stApp .st-key-panel_nodo [data-testid="stFormSubmitButton"] button p,
.stApp .st-key-panel_arista [data-testid="stFormSubmitButton"] button p {
    color: $dorado; font-family: 'Cinzel', serif; font-weight: 700;
}
.st-key-panel_nodo [data-testid="stFormSubmitButton"] button:hover,
.st-key-panel_arista [data-testid="stFormSubmitButton"] button:hover {
    background: rgba(212, 168, 72, .18); border-color: $dorado;
}

/* ----- Campos de texto y listas desplegables (siguen el tema) ----- */
.stApp [data-baseweb="input"] > div,
.stApp [data-testid="stSelectbox"] div:has(> input) {
    background: $input_bg; border-color: $borde;
}
.stApp [data-testid="stSelectbox"] input,
.stApp [data-testid="stTextInput"] input {
    color: $input_texto !important;
    -webkit-text-fill-color: $input_texto;
    background: transparent;
}
.stApp [data-testid="stSelectbox"] button {
    background: transparent; border: none; width: auto;
}
.stApp [data-testid="stSelectbox"] svg { color: $dorado; fill: $dorado; }
[data-testid="stSelectboxVirtualDropdown"] {
    background: $input_bg; border: 1px solid $dorado;
}
.stButton button, .stDownloadButton button {
    background: transparent; border: 1px solid $dorado;
}
.stApp .stButton button p, .stApp .stDownloadButton button p {
    font-family: 'Cinzel', serif; font-weight: 700; color: $texto;
}
.stButton button:hover, .stDownloadButton button:hover {
    background: rgba(212, 168, 72, .15); border-color: $dorado;
}
.stButton button[kind="primary"] {
    background: linear-gradient(180deg, $guinda, #4A0D16);
    border: 1px solid $dorado;
    box-shadow: inset 0 0 0 2px rgba(212, 168, 72, .35);
}
.stApp .stButton button[kind="primary"] p { color: #F3D58A; }
[data-testid="stFileUploaderDropzone"] {
    background: $input_bg; border: 1px dashed $dorado;
}

/* ----- Tablas: encabezado de lacre ----- */
[data-testid="stTable"] table { color: $texto; border-color: $borde; }
[data-testid="stTable"] th {
    background: $guinda; font-family: 'Cinzel', serif; letter-spacing: .4px;
}
/* Letras blancas en encabezados e indices (fondo tinto) */
.stApp [data-testid="stTable"] th,
.stApp [data-testid="stTable"] th * { color: #FFFFFF !important; }
[data-testid="stTable"] td, [data-testid="stTable"] th { border-color: $borde; }
[data-testid="stTable"] tbody tr:nth-child(even) td { background: $fila_par; }

/* ----- Avisos, separadores y notificaciones ----- */
[data-testid="stAlert"] > div {
    background: rgba(184, 137, 46, .12); border-left: 4px solid $dorado;
    color: $texto;
}
[data-testid="stAlert"] p { color: $texto; }
hr {
    border: none !important; height: 1px;
    background: linear-gradient(90deg, transparent, $dorado, transparent);
}
[data-testid="stToast"] {
    background: $madera; border: 1px solid $dorado;
}
.stApp [data-testid="stToast"] *, [data-testid="stToast"] * {
    color: $panel_texto;
}

/* ----- Resultado de Dijkstra ----- */
.stApp .camino {
    font-family: 'Cinzel', serif; font-size: 1.45rem; font-weight: 700;
    color: $acento; letter-spacing: 1px;
}
.stApp .etiqueta { color: $texto_suave; font-style: italic; font-size: 1rem; }
.stApp [data-testid="stMetricValue"],
.stApp [data-testid="stMetricValue"] * { font-family: 'Cinzel', serif; color: $acento; }
</style>
""")


# ===== CSS DEL TEMA =====
def css(tema):
    """Regresa la hoja de estilos con los colores del tema elegido."""
    return _CSS.substitute(PALETAS[tema])


# ===== LIENZO: ACOMODO INICIAL DE LOS NODOS =====
def posiciones_circulares(nodos):
    """Acomoda los nodos en circulo, empezando por la izquierda.
    Regresa {nombre: (x, y)} (despues se pueden arrastrar)."""
    n = len(nodos)
    radio = max(160, 45 * n)
    posiciones = {}
    for i, nombre in enumerate(nodos):
        angulo = math.pi + 2 * math.pi * i / max(n, 1)
        posiciones[nombre] = (radio * math.cos(angulo),
                              radio * math.sin(angulo))
    return posiciones


# ===== LIENZO: PIEZAS, ARISTAS Y TABLERO =====
def pieza_de(indice):
    """Pieza de ajedrez fija para el nodo segun su posicion."""
    return PIEZAS[indice % len(PIEZAS)]


def nodo_pieza(nombre, pieza, texto, titulo, color, x, y, paleta):
    """Nodo de vis-network dibujado como una pieza de ajedrez con su
    nombre (y distancia) debajo."""
    return {
        "id": nombre, "x": x, "y": y, "title": titulo, "shape": "text",
        "label": f"<b>{pieza}</b>\n{texto}",
        "font": {
            "multi": "html", "size": 17, "face": FUENTE_LIENZO,
            "color": color, "strokeWidth": 5, "strokeColor": paleta["lienzo"],
            "bold": {"size": 58, "face": FUENTE_PIEZAS, "color": color,
                     "vadjust": 6},
        },
    }


def arista_lienzo(origen, destino, peso, en_camino, paleta):
    """Arista de vis-network; las del camino mas corto van en dorado."""
    return {
        "from": origen, "to": destino, "label": peso,
        "color": {"color": paleta["dorado"] if en_camino else paleta["arista"],
                  "highlight": paleta["dorado"], "hover": paleta["dorado"]},
        "width": 5 if en_camino else 2,
        "font": {"size": 17, "face": FUENTE_LIENZO, "color": paleta["texto"],
                 "strokeWidth": 6, "strokeColor": paleta["lienzo"],
                 "bold": True},
    }


_HTML_LIENZO = Template("""<!doctype html>
<html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700&display=swap" rel="stylesheet">
<script src="$vis_js"></script>
<style>
  html, body { margin: 0; height: 100%; overflow: hidden; }
  body {
    background-color: $lienzo;
    background-image: conic-gradient($casilla 25%, transparent 0 50%,
                                     $casilla 0 75%, transparent 0);
    background-size: 120px 120px;
  }
  #tablero { width: 100%; height: 100%; }
  #error { font-family: Georgia, serif; color: $texto; padding: 1rem; }
  div.vis-tooltip {
    font-family: Georgia, serif; background: $tarjeta; color: $texto;
    border: 1px solid $dorado; border-radius: 3px;
  }
</style></head>
<body><div id="tablero"></div>
<script>
  function dibujar() {
    if (typeof vis === "undefined") {
      document.body.innerHTML =
        '<div id="error">No se pudo cargar vis-network (revisa tu conexión a internet).</div>';
      return;
    }
    new vis.Network(document.getElementById("tablero"), {
      nodes: new vis.DataSet($nodos),
      edges: new vis.DataSet($aristas)
    }, {
      physics: false,
      interaction: { dragNodes: true, dragView: true, zoomView: true,
                     hover: true },
      edges: { smooth: false, arrows: { to: { enabled: $dirigido } } }
    });
  }
  (document.fonts ? document.fonts.ready : Promise.resolve()).then(dibujar);
</script></body></html>
""")


def html_lienzo(nodos, aristas, dirigido, paleta, alto):
    """HTML del tablero: casillas de ajedrez de fondo y el grafo encima
    (los nodos se pueden arrastrar)."""
    return _HTML_LIENZO.substitute(
        paleta, vis_js=VIS_NETWORK_JS, alto=alto,
        nodos=json.dumps(nodos, ensure_ascii=False),
        aristas=json.dumps(aristas, ensure_ascii=False),
        dirigido="true" if dirigido else "false")
