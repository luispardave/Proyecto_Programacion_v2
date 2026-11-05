"""
Titulo: io_handler
Nombre Completo: Luis Angel Pardave Garcia
Fecha de creación: 29/10/2026
Descripcion: Recaba los inputs del usuario y los guarda en Nodos.csv
"""


import csv
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

        if origen == destino:
            print("Error: El origen y el destino no pueden ser iguales.")
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
        writer = csv.DictWriter(file, fieldnames=ENCABEZADOS)
        writer.writeheader()
        writer.writerows(conexiones)
    print("Conexiones guardadas en Nodos.csv")


# ===== CSV: BORRAR REGISTRO DE Nodos.csv =====
def limpiar_csv():
    """Borra el registro de Nodos.csv dejando solo los encabezados."""
    try:
        with open(RUTA_CSV, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=ENCABEZADOS)
            writer.writeheader()
        print("Registro de Nodos.csv borrado.")
    except PermissionError:
        print("Error: No hay permisos para limpiar Nodos.csv")
