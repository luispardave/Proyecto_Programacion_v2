"""
Titulo: main
Nombre Completo: Luis Angel Pardave Garcia
Fecha de creación: 29/10/2026
Descripcion: Archivo principal, recaba inputs, guarda en CSV y ejecuta
             Dijkstra
"""


import io_handler
from grafo import Grafo


# ===== SALIDA: MOSTRAR RECORRIDO Y PESO =====
def mostrar_resultado(grafo, inicio, destino, distancia, camino):
    """Muestra el recorrido completo tramo por tramo y su peso total."""
    print("\n===== RESULTADO =====")
    if not camino:
        print(f"No existe un camino de {inicio} a {destino}.")
        return

    print("Recorrido completo:")
    acumulado = 0
    for i in range(len(camino) - 1):
        origen = camino[i]
        siguiente = camino[i + 1]
        peso = grafo.nodos[origen].vecinos[siguiente]
        acumulado += peso
        print(f"  {i + 1}. {origen} -> {siguiente} | peso: {peso} "
              f"| acumulado: {acumulado}")

    print(f"Camino: {' -> '.join(camino)}")
    print(f"Peso total de {inicio} a {destino}: {distancia}")


# ===== FLUJO: UNA VUELTA COMPLETA (INPUT -> CSV -> DIJKSTRA) =====
def ejecutar_vuelta():
    """Ejecuta una vuelta completa del programa."""
    # 1. Recabar inputs y guardarlos en Nodos.csv
    conexiones = io_handler.pedir_conexiones()
    io_handler.guardar_csv(conexiones)

    # 2. Instanciar el grafo leyendo Nodos.csv
    grafo = Grafo()
    grafo.cargar_csv(io_handler.RUTA_CSV)

    if not grafo.nodos:
        print("Error: El grafo no tiene nodos.")
        return

    # 3. Ejecutar Dijkstra, se puede repetir con los mismos nodos
    while True:
        inicio, destino = io_handler.pedir_ruta(list(grafo.nodos))
        distancia, camino = grafo.dijkstra(inicio, destino)
        mostrar_resultado(grafo, inicio, destino, distancia, camino)

        otra = input("\n¿Reiniciar el recorrido con los mismos nodos? "
                     "(s/n): ").strip().lower()
        if otra != "s":
            break


# ===== MENU PRINCIPAL (REPETIR VUELTAS) =====
def main():
    try:
        while True:
            try:
                ejecutar_vuelta()
            except FileNotFoundError:
                print("Error: No se encontro el archivo Nodos.csv")
            except PermissionError:
                print("Error: No hay permisos para usar Nodos.csv "
                      "(¿esta abierto en otro programa?)")
            except KeyError as e:
                print(f"Error: Falta la columna {e} en Nodos.csv")
            except ValueError as e:
                print(f"Error: Nodos.csv tiene un dato invalido: {e}")
            except Exception as e:
                print(f"Error inesperado: {type(e).__name__} - {e}")
            finally:
                # 4. Borrar el registro para la siguiente vuelta
                io_handler.limpiar_csv()

            otra = input("\n¿Hacer otra vuelta con nodos nuevos? "
                         "(s/n): ").strip().lower()
            if otra != "s":
                print("Saliendo del programa...")
                break

    # Ctrl + C o fin de entrada en cualquier momento
    except (KeyboardInterrupt, EOFError):
        print("\nPrograma interrumpido por el usuario.")


if __name__ == "__main__":
    main()
