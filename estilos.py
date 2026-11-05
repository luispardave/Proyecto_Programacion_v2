"""
Titulo: estilos
Nombre Completo: Luis Angel Pardave Garcia
Fecha de creación: 05/11/2026
Descripcion: Paletas de color (Light / Dark) y CSS de la web app
"""


from string import Template


# ===== PALETAS DE COLOR =====
PALETAS = {
    "Light": {
        "fondo": "#F6F1E9",
        "tarjeta": "#FFFFFF",
        "texto": "#2A1A16",
        "texto_suave": "#6B5A52",
        "guinda": "#4A0E1A",
        "sidebar": "#3A0A14",
        "dorado": "#C9A063",
        "panel": "#3B2418",
        "panel_texto": "#F6F1E9",
        "borde": "#E3D8C8",
        "grid": "#ECE4D6",
        "lienzo": "#FFFDF9",
        "nodo_bg": "#FFFFFF",
        "nodo_borde": "#4A0E1A",
        "nodo_texto": "#2A1A16",
        "arista": "#3B2418",
        "input_bg": "#FFFFFF",
        "input_texto": "#2A1A16",
        "acento": "#4A0E1A",
    },
    "Dark": {
        "fondo": "#16100E",
        "tarjeta": "#221815",
        "texto": "#F1E8DC",
        "texto_suave": "#B8A89A",
        "guinda": "#7A1C2E",
        "sidebar": "#2B0710",
        "dorado": "#D4AF6E",
        "panel": "#2E1C14",
        "panel_texto": "#F1E8DC",
        "borde": "#3A2A24",
        "grid": "#2A1F1B",
        "lienzo": "#1C1411",
        "nodo_bg": "#2A1F1B",
        "nodo_borde": "#D4AF6E",
        "nodo_texto": "#F1E8DC",
        "arista": "#B8A89A",
        "input_bg": "#2A1F1B",
        "input_texto": "#F1E8DC",
        "acento": "#D4AF6E",
    },
}


# ===== CSS (se rellena con la paleta del tema activo) =====
_CSS = Template("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');

html, body, .stApp { font-family: 'Roboto', sans-serif; }
.stApp { background: $fondo; color: $texto; }
[data-testid="stHeader"] { background: transparent; }

/* Textos generales */
.stApp h1, .stApp h2, .stApp h3, .stApp h4,
.stMarkdown, .stMarkdown p, .stMarkdown li,
[data-testid="stWidgetLabel"] p,
[data-testid="stMetricValue"], [data-testid="stMetricLabel"] p,
[data-testid="stCaptionContainer"], .stApp label { color: $texto; }
[data-testid="stCaptionContainer"] { color: $texto_suave; }

/* ----- Barra lateral (menu) ----- */
[data-testid="stSidebar"] { background: $sidebar; }
[data-testid="stSidebar"] * { color: #F6F1E9; }
.titulo-app {
    font-size: 1.35rem; font-weight: 700; letter-spacing: .5px;
    padding: .4rem 0 1.2rem 0;
}
[data-testid="stSidebar"] [role="radiogroup"] { gap: .25rem; width: 100%; }
[data-testid="stSidebar"] [role="radiogroup"] label {
    width: 100%; padding: .7rem .9rem; border-radius: 4px;
    border-left: 4px solid transparent; cursor: pointer;
}
[data-testid="stSidebar"] [role="radiogroup"] label > div:first-child {
    display: none;
}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
    background: rgba(0, 0, 0, .28); border-left-color: $dorado;
}
[data-testid="stSidebar"] [role="radiogroup"] label:hover {
    background: rgba(0, 0, 0, .18);
}
[data-testid="stSidebar"] [role="radiogroup"] p { font-size: 1.05rem; }

/* ----- Encabezado ----- */
.encabezado { font-size: 1.15rem; padding-top: .35rem; }
.encabezado b { color: $texto; }

/* ----- Tarjeta principal ----- */
.st-key-tarjeta {
    background: $tarjeta; border-radius: 10px; padding: 1.4rem 1.6rem;
    box-shadow: 0 2px 10px rgba(0, 0, 0, .08); border: 1px solid $borde;
}
.titulo-panel { font-weight: 700; font-size: 1.2rem; margin-bottom: .6rem; }

/* ----- Lienzo del grafo (cuadricula) ----- */
.st-key-lienzo {
    border: 1px solid $dorado; border-radius: 8px; padding: .5rem .7rem;
    background-color: $lienzo;
    background-image:
        linear-gradient($grid 1px, transparent 1px),
        linear-gradient(90deg, $grid 1px, transparent 1px);
    background-size: 40px 40px;
}
.st-key-lienzo iframe { background: transparent; }
.lienzo-titulo { color: $texto; font-size: .95rem; }

/* ----- Paneles oscuros (Agregar Nodo / Arista) ----- */
.st-key-panel_nodo, .st-key-panel_arista {
    background: $panel; border-radius: 10px; padding: 1.1rem 1.2rem;
    box-shadow: 0 3px 10px rgba(0, 0, 0, .25);
}
.st-key-panel_nodo *, .st-key-panel_arista * { color: $panel_texto; }
.st-key-panel_nodo [data-testid="stForm"],
.st-key-panel_arista [data-testid="stForm"] { border: none; padding: 0; }
.st-key-panel_nodo input, .st-key-panel_arista input,
.st-key-panel_nodo [data-baseweb="select"] *,
.st-key-panel_arista [data-baseweb="select"] * { color: #2A1A16; }
.st-key-panel_nodo [data-baseweb="input"] > div,
.st-key-panel_arista [data-baseweb="input"] > div,
.st-key-panel_arista [data-baseweb="select"] > div { background: #FFFFFF; }
.st-key-panel_nodo button, .st-key-panel_arista button {
    background: transparent; border: 1px solid $dorado; width: 100%;
}
.st-key-panel_nodo button p, .st-key-panel_arista button p { color: $dorado; }
.st-key-panel_nodo button:hover, .st-key-panel_arista button:hover {
    background: rgba(201, 160, 99, .15); border-color: $dorado;
}

/* ----- Inputs y botones generales ----- */
.st-key-tarjeta [data-baseweb="input"] > div,
.st-key-tarjeta [data-baseweb="select"] > div {
    background: $input_bg; border-color: $borde;
}
.st-key-tarjeta input, .st-key-tarjeta [data-baseweb="select"] * {
    color: $input_texto;
}
.stButton button, .stDownloadButton button, [data-testid="stFormSubmitButton"] button {
    border-color: $guinda;
}
.stButton button[kind="primary"] { background: $guinda; border-color: $guinda; }
.stButton button[kind="primary"] p { color: #F6F1E9; }
[data-testid="stFileUploaderDropzone"] { background: $input_bg; }

/* ----- Tablas ----- */
[data-testid="stTable"] table { color: $texto; border-color: $borde; }
[data-testid="stTable"] th { background: $guinda; color: #F6F1E9 !important; }
[data-testid="stTable"] td, [data-testid="stTable"] th { border-color: $borde; }

/* ----- Resultado ----- */
.camino {
    font-size: 1.4rem; font-weight: 700; color: $acento;
    letter-spacing: 1px;
}
.etiqueta { color: $texto_suave; font-size: .9rem; }
</style>
""")


# ===== CSS DEL TEMA =====
def css(tema):
    """Regresa la hoja de estilos con los colores del tema elegido."""
    return _CSS.substitute(PALETAS[tema])
