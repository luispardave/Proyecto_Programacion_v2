"""
Titulo: io_handler
Nombre Completo: Luis Angel Pardave Garcia
Fecha de creación: 29/10/2026
Descripcion: Recaba y valida los inputs del usuario, maneja la lista de
             conexiones y lee/guarda el formato CSV (Nodos.csv)
"""


import csv
import io
import os

# ===== CONFIGURACION DEL ARCHIVO CSV =====
RUTA_CSV = os.path.join(os.path.dirname(__file__), "Nodos.csv")
ENCABEZADOS = ["origen", "destino", "peso"]


# ===== EXCEPCIONES PERSONALIZADAS =====
class NodoInvalidoError(Exception):
    """Se lanza cuando el nodo no es una sola letra."""
    pass


class PesoInvalidoError(Exception):
    """Se lanza cuando el peso no es un numero int o float mayor a 0."""
    pass


class ConexionInvalidaError(Exception):
    """Se lanza cuando el origen y el destino de una conexion son iguales."""
    pass


# ===== VALIDACION: NODO DE UNA SOLA LETRA =====
def validar_nodo(texto):
    """Regresa el nodo en mayuscula o lanza NodoInvalidoError."""
    texto = texto.strip().upper()
    if len(texto) != 1 or not texto.isalpha():
        raise NodoInvalidoError("El nodo debe ser una sola letra (ej: A).")
    return texto


# ===== VALIDACION: PESO INT O FLOAT =====
def validar_peso(texto):
    """Regresa el peso como int o float, o lanza PesoInvalidoError."""
    texto = texto.strip()
    # Solo digitos y como maximo un punto decimal
    if not texto.replace(".", "", 1).isdigit():
        raise PesoInvalidoError("El peso debe ser un número (ej: 5 o 2.5).")

    if "." in texto:
        peso = float(texto)
    else:
        peso = int(texto)

    if peso <= 0:
        raise PesoInvalidoError("El peso debe ser mayor a 0.")
    return peso


# ===== VALIDACION: CONEXION ENTRE DOS NODOS DISTINTOS =====
def validar_conexion(origen, destino):
    """Lanza ConexionInvalidaError si el origen y el destino son iguales."""
    if origen == destino:
        raise ConexionInvalidaError(
            "El origen y el destino no pueden ser iguales.")


# ===== FORMATO: NUMEROS PARA MOSTRAR =====
def formato_numero(numero):
    """Muestra 4 en vez de 4.0 y el infinito como simbolo."""
    if numero == float("inf"):
        return "∞"
    if float(numero).is_integer():
        return str(int(numero))
    return str(round(numero, 2))


# ===== LISTA DE CONEXIONES: BUSCAR, AGREGAR Y ELIMINAR =====
def buscar_conexion(conexiones, origen, destino, dirigido=False):
    """Regresa la conexion entre origen y destino (o None). Si el grafo no
    es dirigido, A-B y B-A son la misma conexion."""
    for c in conexiones:
        if c["origen"] == origen and c["destino"] == destino:
            return c
        if not dirigido and c["origen"] == destino and c["destino"] == origen:
            return c
    return None


def agregar_conexion(conexiones, origen, destino, peso, dirigido=False):
    """Agrega la conexion o actualiza su peso si ya existe.
    Regresa True si es nueva y False si solo se actualizo."""
    validar_conexion(origen, destino)
    existente = buscar_conexion(conexiones, origen, destino, dirigido)
    if existente:
        existente["peso"] = peso
        return False
    conexiones.append({"origen": origen, "destino": destino, "peso": peso})
    return True


def quitar_nodo(conexiones, nombre):
    """Regresa las conexiones sin las que tocan al nodo."""
    return [c for c in conexiones if nombre not in (c["origen"], c["destino"])]


def etiqueta_conexion(conexion, dirigido=False):
    """Texto para mostrar una conexion, ej: 'A — B  (peso 4)'."""
    flecha = "→" if dirigido else "—"
    return (f"{conexion['origen']} {flecha} {conexion['destino']}  "
            f"(peso {formato_numero(conexion['peso'])})")


# ===== INPUT: PEDIR NODO =====
def pedir_nodo(mensaje):
    """Pide un nodo hasta que sea valido."""
    while True:
        try:
            return validar_nodo(input(mensaje))
        except NodoInvalidoError as e:
            print(f"Error: {e}")


# ===== INPUT: PEDIR PESO DE LA CONEXION =====
def pedir_peso():
    """Pide un peso hasta que sea valido."""
    while True:
        try:
            return validar_peso(input("Peso de la conexion: "))
        except PesoInvalidoError as e:
            print(f"Error: {e}")


# ===== INPUT: REGISTRO DE CONEXIONES DEL GRAFO =====
def pedir_conexiones():
    """Pide las conexiones del grafo y las regresa en una lista."""
    conexiones = []
    print("\n===== REGISTRO DE CONEXIONES =====")

    while True:
        origen = pedir_nodo("Nodo origen: ")
        destino = pedir_nodo("Nodo destino: ")

        try:
            validar_conexion(origen, destino)
        except ConexionInvalidaError as e:
            print(f"Error: {e}")
            continue

        peso = pedir_peso()
        conexiones.append({"origen": origen, "destino": destino, "peso": peso})

        otra = input("¿Agregar otra conexion? (s/n): ").strip().lower()
        if otra != "s":
            return conexiones


# ===== INPUT: NODO DE INICIO Y DESTINO =====
def pedir_ruta(nodos):
    """Pide el nodo de inicio y el de destino, validando que existan."""
    print(f"\nNodos disponibles: {', '.join(nodos)}")

    while True:
        inicio = pedir_nodo("Nodo de inicio: ")
        fin = pedir_nodo("Nodo de destino: ")
        if inicio in nodos and fin in nodos:
            return inicio, fin
        print("Error: Alguno de los nodos no existe en el grafo.")


# ===== CSV: GUARDAR CONEXIONES EN Nodos.csv =====
def guardar_csv(conexiones):
    """Guarda las conexiones en Nodos.csv (los errores se manejan en main)."""
    with open(RUTA_CSV, mode="w", newline="", encoding="utf-8") as file:
        escribir_csv(file, conexiones)
    print("Conexiones guardadas en Nodos.csv")


# ===== CSV: ESCRIBIR CONEXIONES EN UN ARCHIVO O TEXTO =====
def escribir_csv(destino, conexiones, nodos=()):
    """Escribe encabezados y conexiones en un archivo abierto o StringIO.
    Los nodos sin conexiones se guardan como 'A,,' (sin destino ni peso)."""
    writer = csv.DictWriter(destino, fieldnames=ENCABEZADOS)
    writer.writeheader()
    writer.writerows(conexiones)
    conectados = {c["origen"] for c in conexiones} | {
        c["destino"] for c in conexiones}
    for nombre in nodos:
        if nombre not in conectados:
            writer.writerow({"origen": nombre, "destino": "", "peso": ""})


def conexiones_a_texto(conexiones, nodos=()):
    """Regresa las conexiones (y nodos sueltos) como texto CSV."""
    salida = io.StringIO()
    escribir_csv(salida, conexiones, nodos)
    return salida.getvalue()


# ===== CSV: PERSISTENCIA DEL GRAFO DE LA WEB APP =====
def guardar_grafo_csv(nodos, conexiones, ruta=None):
    """Guarda todo el grafo (conexiones y nodos sueltos) en Nodos.csv."""
    ruta = ruta or RUTA_CSV
    with open(ruta, mode="w", newline="", encoding="utf-8") as file:
        escribir_csv(file, conexiones, nodos)


def cargar_grafo_csv(ruta=None):
    """Lee Nodos.csv y regresa (nodos, conexiones). Si el archivo no
    existe regresa listas vacias; si tiene datos invalidos lanza
    ValueError o KeyError (ver leer_conexiones_texto)."""
    ruta = ruta or RUTA_CSV
    if not os.path.exists(ruta):
        return [], []
    with open(ruta, mode="r", encoding="utf-8-sig") as file:
        return leer_conexiones_texto(file.read())


# ===== CSV: LEER Y VALIDAR CONEXIONES DESDE TEXTO =====
def leer_conexiones_texto(texto):
    """Lee un CSV (origen,destino,peso) y regresa (nodos, conexiones).
    Una fila sin destino ni peso es un nodo sin conexiones.
    Lanza KeyError si falta una columna o ValueError si una fila es
    invalida."""
    nodos = set()
    conexiones = []
    reader = csv.DictReader(io.StringIO(texto))
    for num, row in enumerate(reader, start=2):
        try:
            origen = validar_nodo(row["origen"] or "")
            if not (row["destino"] or "").strip() and \
                    not (row["peso"] or "").strip():
                nodos.add(origen)
                continue
            destino = validar_nodo(row["destino"])
            validar_conexion(origen, destino)
            peso = validar_peso(row["peso"])
        except (NodoInvalidoError, PesoInvalidoError,
                ConexionInvalidaError) as e:
            raise ValueError(f"fila {num}: {e}")
        nodos.update([origen, destino])
        conexiones.append({"origen": origen, "destino": destino,
                           "peso": peso})
    return sorted(nodos), conexiones


# ===== CSV: BORRAR REGISTRO DE Nodos.csv =====
def limpiar_csv():
    """Borra el registro de Nodos.csv dejando solo los encabezados."""
    try:
        with open(RUTA_CSV, mode="w", newline="", encoding="utf-8") as file:
            escribir_csv(file, [])
        print("Registro de Nodos.csv borrado.")
    except PermissionError:
        print("Error: No hay permisos para limpiar Nodos.csv")
