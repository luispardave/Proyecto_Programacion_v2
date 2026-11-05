"""
Titulo: grafo
Nombre Completo: Luis Angel Pardave Garcia
Fecha de creación: 29/10/2026
Descripcion: Clase Grafo con algoritmo de Dijkstra que lee Nodos.csv
"""


import csv


# ===== CLASE NODO =====
class Nodo:
    def __init__(self, nombre):
        self.nombre = nombre
        self.vecinos = {}


# ===== CLASE GRAFO =====
class Grafo:
    def __init__(self):
        self.nodos = {}

    # ----- Agregar un nodo (si no existe) -----
    def agregar_nodo(self, nombre):
        if nombre not in self.nodos:
            self.nodos[nombre] = Nodo(nombre)

    # ----- Agregar conexion entre dos nodos -----
    def agregar_conexion(self, origen, destino, peso):
        self.agregar_nodo(origen)
        self.agregar_nodo(destino)
        self.nodos[origen].vecinos[destino] = peso
        self.nodos[destino].vecinos[origen] = peso

    # ----- Leer Nodos.csv y armar el grafo -----
    def cargar_csv(self, ruta):
        """Lee las conexiones de Nodos.csv (los errores se manejan en main)."""
        with open(ruta, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                peso = float(row["peso"])
                # Conservar el peso como int si no tiene decimales
                if peso.is_integer():
                    peso = int(peso)
                self.agregar_conexion(row["origen"], row["destino"], peso)

    # ----- Algoritmo de Dijkstra (camino mas corto) -----
    def dijkstra(self, inicio, destino):
        distancias = {}
        anteriores = {}
        visitados = set()

        # Inicializar distancias en infinito
        for nombre in self.nodos:
            distancias[nombre] = float("inf")
            anteriores[nombre] = None

        distancias[inicio] = 0

        while len(visitados) < len(self.nodos):
            # Buscar el nodo no visitado con menor distancia
            nodo_actual = None
            menor_distancia = float("inf")

            for nombre in self.nodos:
                if nombre not in visitados:
                    if distancias[nombre] < menor_distancia:
                        menor_distancia = distancias[nombre]
                        nodo_actual = nombre

            if nodo_actual is None:
                break

            if nodo_actual == destino:
                break

            visitados.add(nodo_actual)
            nodo = self.nodos[nodo_actual]

            # Actualizar distancias de los vecinos
            for vecino, peso in nodo.vecinos.items():
                nueva_distancia = distancias[nodo_actual] + peso

                if nueva_distancia < distancias[vecino]:
                    distancias[vecino] = nueva_distancia
                    anteriores[vecino] = nodo_actual

        # Si el destino no es alcanzable no hay camino
        if distancias[destino] == float("inf"):
            return distancias[destino], []

        # Reconstruir el camino desde el destino hacia el inicio
        camino = []
        actual = destino

        while actual is not None:
            camino.append(actual)
            actual = anteriores[actual]

        camino.reverse()
        return distancias[destino], camino
