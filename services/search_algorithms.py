import heapq
import math
from services.graph_connection import GraphManager  # Cambiamos la importación

# Configuración del manager (debería inicializarse en tu aplicación principal)
neo4j_manager = GraphManager(
    "neo4j+s://c547b307.databases.neo4j.io",
    "neo4j",
    "FlX8y9LhsGZdOzn2sPv05t6izI5aB0hiycJCVZQ8r5k"
)

# Variable global para almacenar el grafo en caché
_cached_graph = None
_graph_version = 0

def get_graph(refresh=False):
    global _cached_graph, _graph_version
    if refresh or _cached_graph is None:
        _cached_graph = neo4j_manager.obtain_graph()  # Usamos el manager
        _graph_version += 1
    return _cached_graph, _graph_version

def invalidate_graph_cache():
    global _cached_graph
    _cached_graph = None

def haversine_heuristic(origin, destination, grafo):
    """Calcula la distancia entre dos ciudades usando la fórmula de Haversine"""
    coord1 = grafo[origin]["coordenadas"]
    coord2 = grafo[destination]["coordenadas"]
    lat1, lon1 = coord1["latitud"], coord1["longitud"]
    lat2, lon2 = coord2["latitud"], coord2["longitud"]

    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371
    return c * r

def a_star_search(origin, destination, grafo):
    """Implementación del algoritmo A*"""
    # Cola de prioridad (fringe) para explorar los nodos con menor costo estimado
    fringe = []
    heapq.heappush(fringe, (0, origin)) # Guarda el nodo padre de cada ciudad para reconstruir el camino
    parent = {origin: None}             # Guarda el costo acumulado desde el origen hasta cada ciudad
    actual_cost = {origin: 0}
    
    while fringe:
        actual = heapq.heappop(fringe)[1]
        
        if actual == destination:
            break
        
        for next, cost in grafo[actual]["vecinos"].items():
            new_cost = actual_cost[actual] + cost       # g(n): sacamos el costo total del origen hasta el vecino
            if next not in actual_cost or new_cost < actual_cost[next]:
                actual_cost[next] = new_cost
                prioridad = new_cost + haversine_heuristic(next, destination, grafo)    #Sumamos la distancia real con la estimada
                heapq.heappush(fringe, (prioridad, next))
                parent[next] = actual

    # Reconstruimos el camino desde el destino al origen usando el diccionario 'parent'
    route = []
    actual = destination
    while actual != origin:
        route.append(actual)
        actual = parent.get(actual)
        if actual is None:
            return [], float('inf')  # No hay camino
    route.append(origin)
    route.reverse()
    
    return route, actual_cost.get(destination, float('inf'))

def greedy_search(origin, destination, grafo):
    """Implementación del algoritmo Greedy Best-First Search"""
    # prioriza por heurística (distancia estimada al destino)
    fringe = []
    heapq.heappush(fringe, (0, origin))
    parent = {origin: None}         # Guarda el nodo anterior (padre) de cada nodo visitado
    actual_distance = {origin: 0}   # Guarda la distancia real recorrida desde el origen

    while fringe:
        # Extraemos el nodo con menor heurística (más prometedor)
        actual = heapq.heappop(fringe)[1]
        
        if actual == destination:
            break
        
        for next, distance in grafo[actual]["vecinos"].items():
            if next not in parent:      # Solo visitamos nodos no explorados
                priority = haversine_heuristic(next, destination, grafo)    #Distancia estimada
                heapq.heappush(fringe, (priority, next))
                parent[next] = actual
                actual_distance[next] = actual_distance[actual] + distance

    # Reconstruir el camino y calcular distancia total
    route = []
    total_distance = 0
    actual = destination
    while actual != origin:
        if actual is None:  # No hay camino
            return []
        route.append(actual)
        total_distance += grafo[parent[actual]]["vecinos"][actual]
        actual = parent[actual]
    
    route.append(origin)
    route.reverse()
    
    return route, total_distance

def dijkstra_search(origin, destination, grafo):
    """Implementación del algoritmo de Dijkstra"""    
    # Cola de prioridad: cada elemento es (costo acumulado, nodo)    
    fringe = []
    heapq.heappush(fringe, (0, origin))
    parent = {origin: None}
    actual_cost = {origin: 0}   # Guarda el costo más bajo encontrado hasta cada nodo
    
    while fringe:
        # Extraemos el nodo con menor costo acumulado
        actual = heapq.heappop(fringe)[1]
        
        if actual == destination:
            break
        
        for next, cost in grafo[actual]["vecinos"].items():
            new_cost = actual_cost[actual] + cost
            # Si es un nuevo nodo o encontramos un camino más corto
            if next not in actual_cost or new_cost < actual_cost[next]:
                actual_cost[next] = new_cost
                heapq.heappush(fringe, (new_cost, next))
                parent[next] = actual

    # Reconstruir el camino
    route = []
    actual = destination
    while actual != origin:
        route.append(actual)
        actual = parent.get(actual)
        if actual is None:
            return [], float('inf')  # No hay camino
    route.append(origin)
    route.reverse()
    
    return route, actual_cost.get(destination, float('inf'))    

def search_route(algorithm, origin, destination):
    """Función principal para ejecutar búsquedas"""
    try:
        grafo, _ = get_graph(refresh=True)
        
        # Validar ciudades antes de buscar
        if origin not in grafo:
            raise ValueError(f"Ciudad origen '{origin}' no encontrada")
        if destination not in grafo:
            raise ValueError(f"Ciudad destino '{destination}' no encontrada")
        
        if algorithm == 1:
            return a_star_search(origin, destination, grafo)
        elif algorithm == 2:
            return greedy_search(origin, destination, grafo)
        elif algorithm == 3:
            return dijkstra_search(origin, destination, grafo)
        else:
            raise ValueError("Algoritmo no válido. Use 1 (A*), 2 (Greedy) o 3 (Dijkstra)")
            
    except Exception as e:
        print(f"Error en search_route: {str(e)}")
        raise