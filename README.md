# ALGO-VISUALIZER // Dijkstra Pathfinder

Web app en Streamlit para crear un grafo, verlo en un lienzo interactivo y
calcular el camino más corto con el algoritmo de Dijkstra.

## Cómo ejecutarla

```
pip install -r requirements.txt
streamlit run app.py
```

## Secciones

1. **Crear Grafo**: agrega nodos (una letra) y aristas con peso; los nodos se pueden arrastrar en el lienzo.
2. **Matriz/Tabla**: matriz de adyacencia, tabla de conexiones, eliminar elementos e importar/exportar CSV.
3. **Ejecutar Dijkstra**: elige inicio y destino; resalta el camino y muestra el recorrido tramo por tramo.
4. **Historial**: recorridos ejecutados en la sesión.
5. **Ajustes**: grafo dirigido / no dirigido, grafo de ejemplo y reinicio.

La versión de consola original sigue disponible con `python main.py`.
